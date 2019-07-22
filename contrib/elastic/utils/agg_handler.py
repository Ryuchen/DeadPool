#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 15:33 
# @Author : ryuchen
# @Site :  
# @File : agg_handler.py 
# @Desc : 
# ==================================================


def has_buckets(sub_dict):
    if isinstance(sub_dict, dict):
        if 'buckets' in sub_dict.keys():
            return True
    return False


class AggResultHandler(object):

    def __init__(self, data, fields):
        self.data = data
        self.agg_min_level = 2
        for level in data:
            try:
                self.agg_min_level = int(level)
            except ValueError:
                pass
            break
        self.fields = fields
        self.filed_num = len(self.fields)
        self.mdi_data = [None for n in range(self.filed_num + self.agg_min_level)]
        self.agg_max_level = len(self.mdi_data) - 2
        self.rlt_list = list()

    def handle(self, sub_tree, row):
        for node in sub_tree:
            if has_buckets(sub_tree[node]) and len(sub_tree[node]["buckets"]) > 0:
                # buckets terms
                if isinstance(sub_tree[node]["buckets"], list):
                    for branch in sub_tree[node]["buckets"]:
                        row.update({node: branch["key"]})
                        index = int(node)
                        self.mdi_data[index] = branch["key"]
                        if index == self.agg_max_level:
                            self.mdi_data[self.agg_max_level + 1] = branch["doc_count"]
                            yield self.mdi_data[self.agg_min_level:]
                        for item in self.handle(branch, row):
                            yield item

                # buckets filters
                elif isinstance(sub_tree[node]["buckets"], dict):
                    for branch in sub_tree[node]["buckets"]:
                        row.update({node: branch})
                        for item in self.handle(sub_tree[node]["buckets"][branch], row):
                            yield item

    def get_dicts(self):
        for item in self.handle(self.data, {}):
            self.rlt_list.append(dict(zip(self.fields, item)))
        return self.rlt_list

    def get_lists(self):
        for item in self.handle(self.data, {}):
            self.rlt_list.append(item)
        return self.rlt_list
