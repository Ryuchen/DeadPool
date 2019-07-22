#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# File: AggRiskHostBase
# Date: 2019/4/16
# Creator: chen
# Description: ...
# ==================================================
from common.timetrans import *
from elasticsearch import helpers
from apps.periodic.base import BaseTask
from datetime import timedelta, datetime
from elasticsearch_dsl import Search, Q, A
from contrib.elastic.query.es_host_aggtask import ESHostAggTask


class PeriodicTask(BaseTask):
    abstract = True  # This configuration to tell celery this is not the task.

    last_time = (datetime.now() - timedelta(days=7)).replace(second=0, microsecond=0)
    this_time = datetime.now().replace(second=0, microsecond=0)

    # Initialise the elasticsearch connection
    es_agg_task = ESHostAggTask()

    def agg_alarms(self, start_time, end_time, host_type='src', size=10000):
        s = Search(using=self.es_session.es_client, index=self.es_session.indices).params(ignore=[404])
        timestamp_range = {
            "gte": int(start_time * 1000),
            "lt": int(end_time * 1000),
            "format": "epoch_millis"
        }
        q_range = Q("range", last_happened=timestamp_range)
        must = [
            Q({'term': {'{0}.is_asset'.format(host_type): True}})
        ]
        q_bool = Q('bool', must=must)
        s = s.query(q_range).query(q_bool)

        s.aggs.bucket('host_agg', A('terms', field='{0}.ip'.format(host_type), size=size)) \
            .metric('host_group', A({
                'top_hits': {
                    'sort': [{'last_happened': {'order': 'desc'}}],
                    '_source': {'includes': ['last_happened', '{0}.host_group'.format(host_type),
                                             '{0}.top_device_type'.format(host_type),
                                             '{0}.device_type'.format(host_type),
                                             '{0}.asset_value'.format(host_type)]},
                    'size': 1
                }
            })) \
            .metric('alarm_rules', A('terms', field='rule', size=size)) \
            .metric('max_severity', A('max', field='severity')) \
            .metric('max_com_rel', A('max', field='{0}.com_rel'.format(host_type))) \
            .metric('last_happened', A('max', field='last_happened'))

        s = s.extra(size=size)
        res = s.execute()
        aggs = res.aggregations.to_dict()
        data = aggs.get('host_agg', {}).get('buckets', [])
        return data

    def merge_host(self, src, dst):
        data = []
        existed_host = []

        for item in src + dst:
            if item.get('key') not in existed_host:
                existed_host.append(item.get('key'))
                alarm_rules = []
                for bucket in item.get('alarm_rules').get('buckets'):
                    alarm_rules.append({'key': bucket.get('key'), 'count': bucket.get('doc_count')})

                # if item.get('device_type', {}).get('hits').get('total', 0) > 0:
                #     if item.get('device_type', {}).get('hits').get('hits')[0].get('_source').get('src'):
                #         device_type = item.get('device_type', {}).get('hits').get('hits')[0].get('_source').get(
                #             'src').get('device_type')
                #     elif item.get('device_type', {}).get('hits').get('hits')[0].get('_source').get('dst'):
                #         device_type = item.get('device_type', {}).get('hits').get('hits')[0].get('_source').get(
                #             'dst').get('device_type')
                #     else:
                #         device_type = ''
                # else:
                #     device_type = ''
                # if item.get('top_device_type', {}).get('hits').get('total', 0) > 0:
                #     if item.get('top_device_type', {}).get('hits').get('hits')[0].get('_source').get('src'):
                #         top_device_type = item.get('top_device_type', {}).get('hits').get('hits')[0].get('_source').get(
                #             'src').get('top_device_type')
                #     elif item.get('top_device_type', {}).get('hits').get('hits')[0].get('_source').get('dst'):
                #         top_device_type = item.get('top_device_type', {}).get('hits').get('hits')[0].get('_source').get(
                #             'dst').get('top_device_type')
                #     else:
                #         top_device_type = ''
                # else:
                #     top_device_type = ''
                asset_value = 2
                if item.get('host_group', {}).get('hits').get('total', 0) > 0:
                    if item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get('src'):
                        host_group = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'src').get('host_group')
                        device_type = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'src').get('device_type')
                        top_device_type = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'src').get('top_device_type')
                        asset_value = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'src').get('asset_value')
                    elif item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get('dst'):
                        host_group = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'dst').get('host_group')
                        device_type = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'dst').get('device_type')
                        top_device_type = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'dst').get('top_device_type')
                        asset_value = item.get('host_group', {}).get('hits').get('hits')[0].get('_source').get(
                            'dst').get('asset_value')
                    else:
                        host_group = ''
                        device_type = ''
                        top_device_type = ''
                        asset_value = 2
                else:
                    host_group = ''
                    device_type = ''
                    top_device_type = ''
                    asset_value = 2

                # add  dynamic  delta  com_rel
                delta_rel = len(alarm_rules) - 1
                final_com_rel = min(int(item.get('max_com_rel').get('value')) + delta_rel, 10)

                data.append({
                    'alarm_count': item.get('doc_count', 0) + 0,
                    'last_happened': long(item.get('last_happened').get('value')),
                    'host': item.get('key'),
                    'severity': int(item.get('max_severity').get('value')),
                    'com_rel': final_com_rel,
                    'top_device_type': top_device_type,
                    'device_type': device_type,
                    'alarm_rules': alarm_rules,
                    'host_group': host_group,
                    'status': 0,
                    'asset_value': asset_value
                })
            else:
                existed = data[existed_host.index(item.get('key'))]
                alarm_rules = existed.get('alarm_rules')
                existed_alarms = {}
                for alarm in alarm_rules:
                    existed_alarms[alarm.get('key')] = alarm.get('count')
                cur_item_rule_count = 0
                for bucket in item.get('alarm_rules').get('buckets'):
                    cur_item_rule_count += 1
                    if bucket.get('key') in existed_alarms:
                        existed_alarms[bucket.get('key')] += bucket.get('doc_count', 0)
                    else:
                        existed_alarms[bucket.get('key')] = bucket.get('doc_count') + 0
                alarm_rules = []
                for k, c in existed_alarms.items():
                    alarm_rules.append({'key': k, 'count': c})
                # add  dynamic  delta  com_rel
                delta_rel = cur_item_rule_count - 1
                final_com_rel = min(
                    int(max(int(item.get('max_com_rel').get('value')) + delta_rel, existed.get('com_rel'))), 10)

                data[existed_host.index(item.get('key'))] = {
                    'alarm_count': existed.get('alarm_count', 0) + item.get('doc_count', 0),
                    'last_happened': long(max(item.get('last_happened').get('value'), existed.get('last_happened'))),
                    'host': item.get('key'),
                    'severity': int(max(item.get('max_severity').get('value'), existed.get('severity'))),
                    'com_rel': final_com_rel,
                    'top_device_type': existed.get('top_device_type'),
                    'device_type': existed.get('device_type'),
                    'alarm_rules': alarm_rules,
                    'host_group': existed.get('host_group'),
                    'status': 0,
                    'asset_value': existed.get('asset_value')
                }
        return data

    def bulk_insert(self, index, data_list):
        docs = map(lambda item: {
            '_index': index,
            '_type': 'host-risk',
            '_source': item
        }, data_list)
        res = helpers.bulk(self.es_session.es_client, docs)
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
                "max_time": {
                    "max": {
                        "field": "end_time"
                    }
                }
            }
        })
        response = None
        if ret.hits.total > 0:
            response = ret.aggregations
        return response

    def run(self, *args, **kwargs):
        result = []
        response = self.get_last_run_info(self.this_time)
        last_timestamp = None
        if response:
            last_timestamp = response['max_time']['value']
        self.this_time = self.request.kwargs.get("datetime", datetime.now())

        # The last task running time.
        # if the first time to running this task, there will be no task last time.
        start_time = self.last_time
        end_time = self.this_time
        if last_timestamp:
            start_time = timestamp2datetime(last_timestamp)

        if self.options.get("source", "elasticsearch") == "elasticsearch":
            seek_indices_prefix = self.options.get("seek", "host-alarm")
            sink_indices_prefix = self.options.get("sink", "host-risk")

            self.es_session.prefix = seek_indices_prefix
            self.es_session.gedices(start=start_time, end=end_time)

            start_timestamp = datetime2timestamp(start_time)
            end_timestamp = datetime2timestamp(end_time)
            src_host = self.agg_alarms(start_time=start_timestamp, end_time=end_timestamp, host_type='src')
            dst_host = self.agg_alarms(start_time=start_timestamp, end_time=end_timestamp, host_type='dst')
            risk_hosts = self.merge_host(src=src_host, dst=dst_host)
            sink_index = '{0}-{1}'.format(sink_indices_prefix, start_time.strftime('%Y-%m-%d'))

            self.bulk_insert(index=sink_index, data_list=risk_hosts)

            result.append({
                'risk_host_cnt': len(risk_hosts),
                'start_time': int(start_timestamp * 1000),
                'end_time': int(end_timestamp * 1000)
            })
            return result
