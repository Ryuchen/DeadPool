#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-14 22:45 
# @Author : ryuchen
# @Site :  
# @File : IPInfo.py 
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import
import netaddr
import MySQLdb
import logging

log = logging.getLogger("default")


class IPInfo:
    def __init__(self):
        self.networks = []
        self.device_type = {}
        self.host_groups = {}
        self.asset_networks = []
        self.get_assets_info()
        self._get_asset_networks()
        self.ip_cache = {}
        pass

    def get_assets_info(self):
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="12345678*", db="website", charset="utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        sql = ' select d1.id as device_type_id, d1.type as sub, d2.type as top,d2.id as top_id, bde_assets_network.* ' \
              ' from device_type d1 ' \
              ' left join device_type d2 on d1.parent_id=d2.id ' \
              ' join bde_assets_network on d1.id = bde_assets_network.device_type '
        cursor.execute(sql)
        rows = cursor.fetchall()
        self.networks = rows

        sql = ' select d1.id as id, d1.type as sub, d2.type as top ' \
              ' from device_type d1 ' \
              ' left join device_type d2 on d1.parent_id=d2.id '
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            cur_type = {'sub': row['sub'], 'top': row['top']}
            self.device_type[row['id']] = cur_type

        sql = 'select id,group_name from host_group'
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            self.host_groups[row['id']] = row['group_name']

        cursor.close()
        conn.close()

    def _get_asset_networks(self):
        ip_list = []
        for network in self.networks:
            ip_list.append(netaddr.IPNetwork(network.get('cidr')))
        self.asset_networks = netaddr.cidr_merge(ip_list)

    def is_asset(self, ip):
        for network in self.asset_networks:
            if netaddr.IPAddress(ip) in network:
                return True
        return False

    def get_asset_network(self, ip):
        for network in self.networks:
            try:
                if netaddr.IPAddress(ip) in netaddr.IPNetwork(network.get('cidr')):
                    return network
            except Exception as e:
                pass
        return None

    def update_cache(self, ips):
        # update cache
        if len(ips) <= 0:
            return
        step = 500
        conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="12345678*", db="website", charset="utf8")
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        if len(ips) < step:
            self._update_step_cache(cursor, ips)
        else:
            index_start = 0
            ipList = list(ips)
            while index_start < len(ipList):
                self._update_step_cache(cursor, ipList[index_start: index_start + step])
                index_start += step
        cursor.close();
        conn.close();

    def _update_step_cache(self, cursor, ips):
        format_strings = ','.join(['%s'] * len(ips))
        sql = ' select ip,asset_value,device_type_id,group_id' \
              ' from host ' \
              ' where ip in (%s)'
        cursor.execute(sql % format_strings, tuple(ips))
        rows = cursor.fetchall()
        for row in rows:
            ip_info = {}
            ip_info['asset_value'] = row['asset_value']
            ip_info['top'] = self.device_type[row['device_type_id']]['top']
            ip_info['sub'] = self.device_type[row['device_type_id']]['sub']
            if row['group_id'] in self.host_groups:
                ip_info['group_name'] = self.host_groups[row['group_id']]
            else:
                ip_info['group_name'] = self.host_groups[-1] if ip_info['top'] == 1 else self.host_groups[-2]
            self.ip_cache[row['ip']] = ip_info

    def get_ip_info(self, ip):
        if ip in self.ip_cache:
            return True, self.ip_cache[ip]['top'], self.ip_cache[ip]['sub'], \
                   self.ip_cache[ip]['group_name'], self.ip_cache[ip]['asset_value']
        else:
            try:
                if not self.is_asset(ip):
                    return False, '', '', '', 0
                else:
                    auto_detect_ids = [68, 69]  # automatic detect ids
                    network = self.get_asset_network(ip)
                    top = self.device_type[9]['top']
                    sub = self.device_type[9]['sub']
                    host_group = self.host_groups[-2]
                    if not network.get('device_type_id') in auto_detect_ids:
                        top = network.get('top')
                        sub = network.get('sub')
                        host_group = self.host_groups[-1] if network.get('top_id') == 1 else self.host_groups[-2]
                    return True, top, sub, host_group, 2  # 2 is default asset value
            except Exception as e:
                log.error(msg='failed to get host info, {0}, the ip is: {1}, '.format(str(e), ip))
        return False, '', '', '', 0
