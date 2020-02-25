#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:37
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : crawler
# @Desc : 
# ==================================================
import re
import time
import traceback

from celery.task import Task
from celery.utils.log import get_task_logger

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

logger = get_task_logger(__name__)


class TmallCrawler(Task):

    def __init__(self, target):
        self.target = target

        # 爬取的页面总数
        self.total_page = 1
        self.current_page = 1

    def resume(self):
        # 获取之前中断的页面位置
        if self.target.get('stage', '') != '':
            self.current_page = self.target['stage']

    def search(self, cargo):
        # 等待该页面input输入框加载完毕
        input_widget = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tm-nav-2015-new > div.tm-nav > div.tm-search > div.mall-search > form.mallSearch-form > fieldset > div.mallSearch-input > div.s-combobox > div.s-combobox-input-wrap > input.s-combobox-input')))
        submit_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tm-nav-2015-new > div.tm-nav > div.tm-search > div.mall-search > form.mallSearch-form > fieldset > div.mallSearch-input > button')))
        input_widget.clear()
        input_widget.send_keys(cargo)
        # 强制延迟1秒，防止被识别成机器人
        time.sleep(1)
        submit_btn.click()

    def page_total(self):
        # 商品列表页 总页数框
        total_page = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-page-skip > form')))
        total_page = total_page.text
        # 清洗获取总页数
        self.total_page = int(re.match('.*?(\d+).*', total_page).group(1))

    def page_prev(self):
        # 获取 上一页的按钮 并 点击
        prev_page_submit = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-num > a.ui-page-prev')))
        prev_page_submit.click()

    def page_next(self):
        # 获取 下一页的按钮 并 点击
        next_page_submit = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-num > a.ui-page-next')))
        next_page_submit.click()

    def run(self, *args, **kwargs):
        # 对每一个项目的爬取过程进行状态记录，记录爬取的页数
        # 将最终结果替换之前的对应位置上的记录
        # 输入名称的查询方法
        logger.info('当前爬取的项目是：『{}』'.format(self.target['name']))
        try:
            self.search(self.target['name'])
            # 获取 商品列表页 总页数
            self.page_total()
            while self.current_page < self.total_page:  # 遍历 前多少页的 商品列表页
                # 跳过之前已经爬取过的页面
                if page_count != self.current_page:
                    self.slideDown()  # 执行 下拉动作
                    self.page_next()  # 执行 按下一页按钮 动作
                    self.sliderVerification()  # 检测是否有 滑块验证
                    page_count += 1
                else:
                    # 确认 当前商品列表页 的 全部商品 都 加载完成
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '#J_ItemList .product .product-iWrap')))
                    # 获取 当前页面的 源代码
                    html = self.browser.page_source
                    doc = pq(html)
                    goods_items = doc('#J_ItemList .product').items()  # 获取 当前页 全部商品数据
                    for _ in goods_items:  # 遍历 全部商品数据
                        goods_title = _.find('.productTitle').text().replace('\n', '')
                        goods_sales_volume = _.find('.productStatus span').text()
                        goods_price = _.find('.productPrice').text().replace('¥\n', '')
                        goods_shop = _.find('.productShop').text().replace('\n', '')
                        goods_url = ''.join(['https:', _.find('.productImg').attr('href')])
                        goods_id = re.match('.*?id=?(\d+)&.*', goods_url).group(1)
                        record = ','.join(
                            [goods_id, category['name'], subcategory['name'], item['name'],
                             goods_title, str(goods_price), str(goods_sales_volume),
                             goods_shop, goods_url]
                        )
                        records_file.write('{}\n'.format(record))

                    self.slideDown()
                    self.nextPage()
                    self.sliderVerification()
                    page_count += 1
                    self.current_page += 1
                    temp_item['stage'] = page_count

                time.sleep(2)
            # 如果没有任何错误发生，并且遍历完成了 pages, 则记录该子类已经爬取完成
            temp_item['stage'] = 'finish'
        except:
            traceback.print_exc()
            raise CrawlException
        finally:
            temp_subcategory['subs'][__index] = temp_item
        return document