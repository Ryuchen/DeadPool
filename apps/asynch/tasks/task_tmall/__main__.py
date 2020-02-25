#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-13:56
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : __main__.py
# @Desc : 
# ==================================================
import re
import os
import json
import time
import random
import string
import traceback

from celery import chain

from pyquery import PyQuery as pq
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from apps.asynch.base import BaseTask
from common.sqlitedao import SQLiteDao
from common.exceptions import CrawlException

from .crawler import TmallCrawler
from .middleware import TmallMiddleware
from .pipeline import TmallPipeline


class TaskTmall(BaseTask):

    name = "task_tmall"

    login_url = 'https://login.taobao.com/member/login.jhtml'  # 淘宝登录地址
    target_url = 'https://www.tmall.com/'  # 爬取的目标地址

    table_ddl = '''
 CREATE TABLE IF NOT EXISTS RECORDS
 (
     ID INTEGER PRIMARY KEY AUTOINCREMENT,
     TARGET CHAR(50) NOT NULL,
     STAGE CHAR(50) NOT NULL,
     STORAGE TEXT NOT NULL,
 );
    '''

    def __init__(self):
        super(TaskTmall, self).__init__()
        self.proxy = self.options.get("proxy", False)
        self.nickname = self.options.get("proxy", False)
        self.username = self.options.get("proxy", False)
        self.password = self.options.get("proxy", False)
        self.targets = []

        storage_module = self.options.get("storage", {}).get("module", "FileStorage")
        if storage_module == "FileStorage":
            from common.plugins.storage.filestorage import FileStorage
            # 按配置加载的存储模块实例
            self.module = FileStorage(self.name, self.options.get("storage", {}).get("path", ""))
            # 存储的位置
            self.storage = self.module.storage
        else:
            from common.plugins.storage.mongostorage import MongoStorage
            # 按配置加载的存储模块实例
            self.module = MongoStorage(self.name, self.options.get("storage", {}).get("collection", ""))
            # 存储的位置
            self.storage = self.module.storage

        # # 创建用于爬取记录的sqlite数据库
        # if not os.path.exists(os.path.join('/tmp', '{}-records.db'.format(self.name))):
        #     self.conn = SQLiteDao(os.path.join('/tmp', '{}-records.db'.format(self.name)))
        #     self.conn.create(self.table_ddl)
        #     for _ in self.options.get("keyword"):
        #         sql = "INSERT INTO RECORDS (TARGET, STAGE, STORAGE) VALUES ({}, '-1', 'N/A')".format(_)
        #         self.conn.insert_execute(sql)
        # else:
        #     self.conn = SQLiteDao(os.path.join('/tmp', '{}-records.db'.format(self.name)))

    def login(self):
        self.browser.get(self.login_url)
        # 用css选择器选择 切换淘宝使用账号密码登录按钮
        username_password_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.login-box.no-longlogin.module-quick > .hd > .login-switch')))
        username_password_button.click()
        # 用css选择器选择 使用微博登录按钮
        weibo_button = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))
        weibo_button.click()
        # 用xpath选择器选择 账号框
        input_username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))
        input_username.send_keys(self.username)  # 输入 账号
        # 用xpath选择器选择 密码框
        input_password = self.wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
        input_password.send_keys(self.password)  # 输入 密码
        # 用xpath选择器选择 登录按钮
        login_button = self.wait.until(EC.presence_of_element_located((By.XPATH, '//span[text()="登录"]')))
        login_button.click()
        # 用css选择器选择 淘宝昵称
        taobao_name = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.site-nav-login-info-nick')))
        # 通过输出淘宝的名称判断是否登录成功
        if taobao_name.text == self.nickname:
            print(''.join(['登录成功，淘宝账号为：', taobao_name.text]))
        else:
            print(''.join(['登录失败，淘宝账号为：', taobao_name.text]))

    def resume(self):
        """
        根据启用的存储模型来找寻上一次爬取的中断位置
        :return:
        """
        # self.targets = self.conn.select_execute("SELECT * from RECORDS where STAGE is not 'finish' order by ID")
        pass

    def run(self, *args, **kwargs):
        self.login()
        self.browser.get(self.target_url)

        # TODO: 如何判断网页是否加载完成
        time.sleep(2)

        # 遍历需要进行爬取的种类的清单
        # try:
        #     for index, _ in enumerate(self.targets):
        #         # 声明 与当前一样的 category 对象，后续需要对其进行存储
        #         temp_category = category  # very important 为了实现断点续爬
        #
        #         # 判断当前的大类别是否已经进行了爬取，获取其存储路径
        #         temp_category['storage'] = self.verify_storage(category, storage_path)
        #
        #         print('当前爬取的大类目是：『{}』, 其子类一共 {} 种'.format(category['name'], len(category['subs'])))
        #
        #         # 当发生爬取错误的时候，替换原来的 category 里面对应位置的记录，以更新爬取进度
        #         try:
        #             for _index, subcategory in enumerate(category['subs']):
        #                 # 声明 与当前一样的 subcategory 对象，后续需要对其进行存储
        #                 temp_subcategory = subcategory  # very important 为了实现断点续爬
        #                 # 判断当前的子类别是否已经进行了爬取，获取其存储路径
        #                 temp_subcategory['storage'] = self.verify_storage(subcategory, temp_category['storage'])
        #
        #                 if 'stage' in temp_subcategory:  # 如果当前这个子类已经爬取完了，那么就跳过
        #                     continue
        #
        #                 print('当前爬取的子类目是：『{}』, 其子类一共 {} 种'.format(subcategory['name'], len(subcategory['subs'])))
        #
        #                 # 确认 上次断点的时候在爬取的 项目的进度
        #                 try:
        #                     for __index, item in enumerate(subcategory['subs']):
        #                         # 如果当前这个项目已经爬取完了，那么就跳过这项目
        #                         if item.get('stage', '') == 'finish':
        #                             continue
        #                         else:
        #                             crawler = TmallCrawler(self.search, item)
        #                             middleware = TmallMiddleware()
        #                             pipeline = TmallPipeline()
        #                             job = chain(crawler.s(item), middleware.s(), pipeline.s())()
        #
        #                         # 声明 与当前一样的 item 对象，后续需要对其进行存储
        #                         self.current_page = 1  # 当前爬取的页面
        #                         temp_item = item  # very important 为了实现断点续爬
        #                         write_title = True  # 判断是否需要输入 csv 标题
        #
        #                         if 'stage' in item:
        #                             if item['stage'] == 'finish':  # 如果当前这个项目已经爬取完了，那么就跳过这项目
        #                                 continue
        #                             else:
        #                                 self.current_page = int(item['stage'])
        #
        #                         if 'file' in item:
        #                             file_path = item['file']
        #                             write_title = False
        #                         else:
        #                             temp_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        #                             file_path = os.path.join(temp_subcategory['storage'], '{}.csv'.format(temp_name))
        #                         temp_item['file'] = file_path
        #
        #                         # 对每一个项目的爬取过程进行状态记录，记录爬取的页数
        #                         # 将最终结果替换之前的对应位置上的记录
        #                         try:
        #                             # 输入名称的查询方法
        #                             print('当前爬取的项目是：『{}』'.format(item['name']))
        #                             self.search(item['name'])
        #                             with open(file_path, 'w+') as records_file:
        #                                 # 如果是该文件的第一次输入，则录入 csv 的标题
        #                                 if write_title:
        #                                     title = ','.join(
        #                                         ['商品id', '商品大类', '商品子类', '商品种类', '商品标题', '商品价格', '商品月销量', '店名',
        #                                          '详情页网址', ])
        #                                     records_file.write('{}\n'.format(title))
        #
        #                                 self.page_total()  # 获取 商品列表页 总页数
        #                                 while self.current_page < self.total_page:  # 遍历 前多少页的 商品列表页
        #                                     # 跳过之前已经爬取过的页面
        #                                     if page_count != self.current_page:
        #                                         self.slideDown()  # 执行 下拉动作
        #                                         self.page_next()  # 执行 按下一页按钮 动作
        #                                         self.sliderVerification()  # 检测是否有 滑块验证
        #                                         page_count += 1
        #                                     else:
        #                                         # 确认 当前商品列表页 的 全部商品 都 加载完成
        #                                         self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#J_ItemList .product .product-iWrap')))
        #                                         # 获取 当前页面的 源代码
        #                                         html = self.browser.page_source
        #                                         doc = pq(html)
        #                                         goods_items = doc('#J_ItemList .product').items()  # 获取 当前页 全部商品数据
        #                                         for _ in goods_items:  # 遍历 全部商品数据
        #                                             goods_title = _.find('.productTitle').text().replace('\n', '')
        #                                             goods_sales_volume = _.find('.productStatus span').text()
        #                                             goods_price = _.find('.productPrice').text().replace('¥\n', '')
        #                                             goods_shop = _.find('.productShop').text().replace('\n', '')
        #                                             goods_url = ''.join(['https:', _.find('.productImg').attr('href')])
        #                                             goods_id = re.match('.*?id=?(\d+)&.*', goods_url).group(1)
        #                                             record = ','.join(
        #                                                 [goods_id, category['name'], subcategory['name'], item['name'],
        #                                                  goods_title, str(goods_price), str(goods_sales_volume),
        #                                                  goods_shop, goods_url]
        #                                             )
        #                                             records_file.write('{}\n'.format(record))
        #
        #                                         self.slideDown()
        #                                         self.nextPage()
        #                                         self.sliderVerification()
        #                                         page_count += 1
        #                                         self.current_page += 1
        #                                         temp_item['stage'] = page_count
        #
        #                                     time.sleep(2)
        #                                 # 如果没有任何错误发生，并且遍历完成了 pages, 则记录该子类已经爬取完成
        #                                 temp_item['stage'] = 'finish'
        #                         except:
        #                             traceback.print_exc()
        #                             raise CrawlException
        #                         finally:
        #                             temp_subcategory['subs'][__index] = temp_item
        #                     # 如果没有任何错误发生，并且遍历完成了 items, 则记录该子类已经爬取完成
        #                     temp_subcategory['stage'] = 'finish'
        #                 except CrawlException:
        #                     raise CrawlException
        #                 finally:
        #                     temp_category['subs'][_index] = temp_subcategory
        #             # 如果没有任何错误发生，并且遍历完成了 subcategory, 则记录该大类已经爬取完成
        #             temp_category['stage'] = 'finish'
        #         except CrawlException:
        #             raise CrawlException
        #         finally:
        #             categories[index] = temp_category
        # except CrawlException:
        #     pass
        # finally:
        #     self.browser.quit()
