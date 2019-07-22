#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-14 10:31 
# @Author : ryuchen
# @Site :  
# @File : base.py 
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import
import six
import logging

from datetime import timedelta, datetime
from elasticsearch import helpers
from elasticsearch_dsl import Search, Q, A
from sqlalchemy.exc import SQLAlchemyError

from apps.periodic.base import BaseTask
from common.timetrans import *
from contrib.elastic.query.es_host_aggtask import ESHostAggTask
from contrib.mysql.website.IPInfo import IPInfo
from contrib.mysql.ATDKnowledge.models import AlarmCategory, AlarmAggRule, AlarmClasstype, KillChain

log = logging.getLogger(__name__)


class PeriodicTask(BaseTask):
    """Basic periodic task to store the common functions."""
    abstract = True  # This configuration to tell celery this is not the task.

    #ip_identify = IPInfo()

    # The additional task configurations
    this_time = None

    # Initialise the elasticsearch connection
    es_agg_task = ESHostAggTask()

    # 汇聚相关的通用方法
    def fetch_agg_rules(self):
        session = self.db_session()
        try:
            query = session.query(
                AlarmAggRule,
                AlarmCategory.category_name,
                AlarmClasstype.classtype_name,
                KillChain.name
            )
            query = query.join(AlarmCategory, AlarmAggRule.category_id == AlarmCategory.category_id)
            query = query.join(AlarmClasstype, AlarmAggRule.classtype_id == AlarmClasstype.classtype_id)
            query = query.join(KillChain, AlarmAggRule.kid == KillChain.kid)
            query = query.filter(AlarmAggRule.status == 1, AlarmAggRule.type == 0)
            return query.all()
        except SQLAlchemyError:
            return []
        finally:
            session.close()

    # 汇聚相关的通用方法
    def filter_agg_tasks(self):
        # To check which agg task in database to run.
        rules = self.fetch_agg_rules()
        running_task = []
        minutes = list(self.run_every.minute)
        hours = list(self.run_every.hour)
        for _ in rules:
            if _.AlarmAggRule.classtype_id in self.options.get("classtype_id"):
                # TODO: this data need to fetch from database, each rules has its own steps
                running_minutes = minutes[::_.AlarmAggRule.time_count]
                if _.AlarmAggRule.time_count >= 60:
                    running_hours = hours[::int(_.AlarmAggRule.time_count / 60)]
                else:
                    running_hours = hours[::1]
                if self.this_time.hour in running_hours and self.this_time.minute in running_minutes:
                    running_task.append(_)
        return running_task

    # 汇聚相关的通用方法
    def agg_range(self, task, last_time, this_time):
        """To generate the agg task aggregation time range"""
        # when we have the last running time means this task is not the first time to run.
        if last_time:
            # calculate the agg task interval, so we can get this time our task end time
            #minutes = list(self.run_every.minute)
            #interval = (minutes[-1] - minutes[-2]) * task.AlarmAggRule.time_count
            start_time = last_time
            #end_time = last_time + timedelta(minutes=interval)
            end_time = this_time
        # opposite.
        else:
            start_time = this_time - timedelta(days=7)
            end_time = this_time
        return start_time, end_time

    # 汇聚相关的通用方法
    def agg_alarms(self, agg_keys, size=10000, severity=-1, reliability=-1, **kwargs):
        if not agg_keys:
            return
        s = Search(using=self.es_session.es_client, index=self.es_session.indices).params(ignore=[404])

        # time range
        timestamp_range = {
            "gte": int(datetime2timestamp(kwargs["start_time"]) * 1000),
            "lt": int(datetime2timestamp(kwargs["end_time"]) * 1000),
            "format": "epoch_millis"
        }

        q_range = Q("range", timestamp=timestamp_range)
        s = s.query(q_range)
        # filters
        must = [Q('exists', field='severity'), Q('exists', field='reliability')]
        for k, v in kwargs.items():
            if k != 'query' and type(v) == str:
                kwargs[k] = v.split(',')
        if 'rid' in kwargs:
            must.append(Q('terms', rid=kwargs['rid']))
        if 'category' in kwargs:
            must.append(Q('terms', category=kwargs['category']))
        if 'query' in kwargs:
            json_query = {
                "query_string": {
                    "query": kwargs['query']
                }
            }
            must.append(Q(json_query))
        if must:
            bool_q = Q('bool', must=must)
            s = s.query(bool_q)

        # agg
        if isinstance(agg_keys, six.string_types):
            agg_keys = agg_keys.split(',')
        if len(agg_keys) <= 1:
            agg_obj = A('terms', field=agg_keys[0], size=size)
        else:
            script = []
            for key in agg_keys:
                script.append("doc['{0}'].value".format(key))
            script = "+'-'+".join(script)
            agg_obj = A('terms', script={'inline': script}, size=size)

        s.aggs.bucket('agg1', agg_obj) \
            .metric('max_severity', A('max', field='severity')) \
            .metric('max_reliability', A('max', field='reliability')) \
            .metric('first_happened', A('min', field='timestamp')) \
            .metric('last_happened', A('max', field='timestamp')) \
            .metric('category_set', A('terms', field='category', size=size)) \
            .metric('engine_set', A('terms', field='engine_type', size=size))

        res = s.execute()
        aggs = res.aggregations.to_dict()
        format_agg_res = []
        update_cache = set()
        for bucket in aggs.get('agg1', {}).get('buckets', []):
            ips = bucket.get('key').split('-')
            for ip in ips:
                if ip not in self.ip_identify.ip_cache and ip not in update_cache and self.ip_identify.is_asset(ip):
                    update_cache.add(ip)

        self.ip_identify.update_cache(update_cache)

        for bucket in aggs.get('agg1', {}).get('buckets', []):
            try:
                severity = severity if severity > 0 else bucket['max_severity']['value']
                reliability = reliability if reliability > 0 else bucket['max_reliability']['value']
                ips = bucket.get('key').split('-')
                src_ip = ips[0]
                src_is_asset, top, sub, src_group, asset_value = self.ip_identify.get_ip_info(src_ip)
                src_ip_info = {
                    'ip': src_ip,
                    'is_asset': src_is_asset,
                    'top_device_type': top,
                    'device_type': sub,
                    'host_group': src_group,
                    'asset_value': asset_value,
                    'com_rel': int(kwargs.get('src_com_rel', 0))
                }
                dst_ip_info = {
                    'ip': None,
                    'is_asset': False,
                    'top_device_type': '',
                    'device_type': '',
                    'host_group': '',
                    'asset_value': 0,
                    'com_rel': int(kwargs.get('dst_com_rel', 0))
                }
                if len(ips) > 1:
                    dst_ip = ips[1]
                    dst_is_asset, top, sub, dst_group, asset_value = self.ip_identify.get_ip_info(dst_ip)
                    dst_ip_info = {
                        'ip': dst_ip,
                        'is_asset': dst_is_asset,
                        'top_device_type': top,
                        'device_type': sub,
                        'host_group': dst_group,
                        'asset_value': asset_value,
                        'com_rel': kwargs.get('dst_com_rel')
                    }
                direction = ['in' if src_ip_info.get('is_asset') else 'out',
                             'in' if dst_ip_info.get('is_asset') else 'out']
                direction = '-'.join(direction)
                item = {
                    'start_time': long(timestamp_range['gte']),
                    'end_time': long(timestamp_range['lt']),
                    'first_happened': long(bucket['first_happened']['value']),
                    'last_happened': long(bucket['last_happened']['value']),
                    'tags': map(lambda x: {'key': x['key'], 'doc_count': x['doc_count']},
                                bucket['category_set']['buckets']),
                    'rule': kwargs.get('alarm_rule'),
                    'kill_chain': 'internal-penertration' if direction == 'in-in' else kwargs.get('kill_chain'),
                    'alarm_category': kwargs.get('alarm_category'),
                    'alarm_classtype': kwargs.get('alarm_classtype'),
                    'classification': kwargs.get('classification'),
                    'attack_res': kwargs.get('attack_res'),
                    'com_rel': int(kwargs.get('com_rel')),
                    'event_category': map(lambda x: {'key': x['key'], 'doc_count': x['doc_count']},
                                          bucket['category_set']['buckets']),
                    'engine': map(lambda x: {'key': x['key'], 'doc_count': x['doc_count']},
                                  bucket['engine_set']['buckets']),
                    'severity': int(severity),
                    'reliability': int(reliability),
                    'src': src_ip_info,
                    'dst': dst_ip_info,
                    'direction': direction,
                    'status': 0,
                    'doc_count': bucket['doc_count']
                }
                # only add >=7 alarm
                if int(item['doc_count']) + int(item['com_rel']) >= 1:
                    format_agg_res.append(item)
            except:
                pass

        return format_agg_res

    # 汇聚相关的通用方法
    def bulk_agg_res(self, index, data_list):
        client = self.es_session.es_client
        docs = map(lambda item: {
            '_index': index,
            '_type': '-'.join(index.split('-')[0:2]),
            '_source': item
        }, data_list)
        res = helpers.bulk(client, docs)
        return res

    # Get last run info of the task
    def get_last_run_info(self, running_time):
        # Get indices last 7 days
        self.es_agg_task.gedices(running_time - timedelta(days=7), running_time)
        # Get the rules of this task last running time from the elasticsearch task log
        ret = self.es_agg_task.search({
            "query": {
                "match": {
                    "task_name": self.name
                }
            },
            "size": 0,
            "aggs": {
                "rule_list": {
                    "terms": {
                        "field": "rule_name",
                        "size": 100,
                        "order": {
                            "_term": "desc"
                        }
                    },
                    "aggs": {
                        "max_time": {
                            "max": {
                                "field": "end_time"
                            }
                        }
                    }
                }
            }
        })
        response = None
        if ret.hits.total > 0:
            response = ret.aggregations.rule_list
        return response

    def run(self, *args, **kwargs):
        self.this_time = self.request.kwargs.get("datetime", datetime.now())

        # To check which agg task in database to run.
        running_task = self.filter_agg_tasks()

        # Refresh IPInfo
        self.ip_identify = IPInfo()

        # build task / last run time map
        last_run_map = {}
        # If have task, get last run info
        if len(running_task) > 0 :
            response = self.get_last_run_info(self.this_time)
            if response:
                sub_tasks = response.buckets
                for sub_task in sub_tasks:
                    last_run_map[sub_task['key']] = sub_task['max_time']['value']

        result = []
        for _ in running_task:
            if not _.AlarmAggRule.agg_keys:
                return

            # The last task running time.
            # if the first time to running this task, there will be no task last time.
            last_time = None
            rule_info = "{0}_{1}".format(self.name, _.AlarmAggRule.id)
            if rule_info in last_run_map:
                last_time = timestamp2datetime(last_run_map[rule_info])

            start_time, end_time = self.agg_range(_, last_time, self.this_time)
            alarms = []
            if self.options.get("source", "elasticsearch") == "elasticsearch":
                seek_indices_prefix = self.options.get("seek", "host-threat")
                sink_indices_prefix = self.options.get("sink", "host-default")

                self.es_session.prefix = seek_indices_prefix
                self.es_session.gedices(start=start_time, end=end_time)
                new_alarms = self.agg_alarms(
                    agg_keys=_.AlarmAggRule.agg_keys,
                    severity=_.AlarmAggRule.severity,
                    reliability=_.AlarmAggRule.reliability,
                    start_time=start_time,
                    end_time=end_time,
                    alarm_rule=_.AlarmAggRule.name,
                    alarm_category=_.category_name,
                    alarm_classtype=_.classtype_name,
                    kill_chain=_.name,
                    attack_res=_.AlarmAggRule.attack_result,
                    com_rel=_.AlarmAggRule.com_reliability,
                    src_com_rel=_.AlarmAggRule.s_com_reliability,
                    dst_com_rel=_.AlarmAggRule.d_com_reliability,
                    classification=_.AlarmAggRule.classification,
                    query=_.AlarmAggRule.query
                )
                alarms.extend(new_alarms)
                log.info('--------->', _.AlarmAggRule.name, datetime2string(start_time), datetime2string(end_time), 'results: ', len(alarms))

                if alarms:
                    sink_index = '{0}-{1}'.format(
                        sink_indices_prefix,
                        start_time.date().strftime("%Y-%m-%d"),
                    )
                    self.bulk_agg_res(index=sink_index, data_list=alarms)

            # TODO: add database support
            elif self.options.get("source", "database") == "database":
                seek_table_name = self.options.get("seek", "host_threat")
                sink_table_name = self.options.get("sink", "host_default")

            result.append({
                "rule_name": "{0}_{1}".format(self.name, _.AlarmAggRule.id),
                "start_time": int(datetime2timestamp(start_time) * 1000),
                "end_time": int(datetime2timestamp(end_time) * 1000)
            })

        return result

