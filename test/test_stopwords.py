#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/6/10-16:06
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : test_stopwords
# @Desc :
# ==================================================
import os
import glob

if __name__ == '__main__':
    cur_dir = os.path.dirname(os.getcwd())
    stopwords = []
    print(cur_dir)
    data_sets = glob.glob(os.path.join(cur_dir, 'data', 'stopwords', '*.txt'))
    for item in data_sets:
        with open(item, encoding="utf-8") as f:
            for line in f:
                stopwords.append(line.strip())
    _stopwords = list(set(stopwords))

    print(len(_stopwords))
