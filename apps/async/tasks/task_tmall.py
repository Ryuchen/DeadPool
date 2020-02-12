#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-13:56
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : tmall
# @Desc : 
# ==================================================
import re
import os
import json
import time
import random
import string
import traceback

from pyquery import PyQuery as pq
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from apps.async.base import Abstract


class Tmall(Abstract):
    top_page = 6
    login_url = 'https://login.taobao.com/member/login.jhtml'  # 淘宝登录地址

    def __init__(self, username, password):
        super(Tmall, self).__init__(username, password)
        self.setupChrome()
        self.categories = []

    def login(self):
        self.browser.get(self.login_url)
        username_password_button = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.login-box.no-longlogin.module-quick > .hd > .login-switch')))  # 用css选择器选择 用账号密码登录按钮
        username_password_button.click()  # 点击 用账号密码登录按钮
        weibo_button = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.weibo-login')))  # 用css选择器选择 用微博登录按钮
        weibo_button.click()  # 点击 用微博登录按钮
        input_username = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="username"]')))  # 用xpath选择器选择 账号框
        input_username.send_keys(self.username)  # 输入 账号
        input_password = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))  # 用xpath选择器选择 密码框
        input_password.send_keys(self.password)  # 输入 密码
        login_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="登录"]')))  # 用xpath选择器选择 登录按钮
        login_button.click()  # 点击 登录按钮
        taobao_name = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.site-nav-login-info-nick')))  # 用css选择器选择 淘宝昵称
        print(''.join(['淘宝账号为：', taobao_name.text]))  # 输出 淘宝昵称

    def search(self, cargo):
        # 等待该页面input输入框加载完毕
        input_widget = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                       'div.tm-nav-2015-new > div.tm-nav > div.tm-search > div.mall-search > form.mallSearch-form > fieldset > div.mallSearch-input > div.s-combobox > div.s-combobox-input-wrap > input.s-combobox-input')))
        submit_btn = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                     'div.tm-nav-2015-new > div.tm-nav > div.tm-search > div.mall-search > form.mallSearch-form > fieldset > div.mallSearch-input > button')))
        input_widget.clear()
        input_widget.send_keys(cargo)
        # 强制延迟1秒，防止被识别成机器人
        time.sleep(1)
        submit_btn.click()

    def getPageTotal(self):
        page_total = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-page-skip > form')))  # 用css选择器选择 商品列表页 总页数框
        page_total = page_total.text
        page_total = re.match('.*?(\d+).*', page_total).group(1)  # 清洗
        return page_total

    def nextPage(self):
        # 获取 下一页的按钮 并 点击
        next_page_submit = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.ui-page > div.ui-page-wrap > b.ui-page-num > a.ui-page-next')))
        next_page_submit.click()

    def sliderVerification(self):
        # 每次翻页后 检测是否有 滑块验证
        try:
            slider_button = WebDriverWait(self.browser, 5, 0.5).until(
                EC.presence_of_element_located((By.ID, 'nc_1_n1z')))
            actions = ActionChains(self.browser)
            actions.click_and_hold(slider_button).perform()
            trace = [10, 320]
            for x in trace:
                actions.move_by_offset(xoffset=x, yoffset=random.randint(-3, 3)).perform()
                actions = ActionChains(self.browser)
            time.sleep(1)
            actions.release().perform()
        except:
            print('没有检测到滑块验证码')

    def getCategories(self):
        targets = []
        html = self.browser.page_source  # 获取 当前页面的 源代码
        doc = pq(html)  # pq模块 解析 网页源代码
        categories = doc('dl.J_catagory_item').items()  # 获取 当前页 全部商品数据
        for category in categories:
            main = {
                'name': category.find('h2').text(),
                'subs': []
            }
            for subcategory in category.find('div.tm-category-block').items():
                if '热门品牌' not in subcategory.find('h3').text():
                    sub = {
                        'name': subcategory.find('h3').text(),
                        'subs': []
                    }
                    for item in subcategory.find('a').items():
                        temp = {'name': item.text(), 'href': item.attr('href')}
                        sub['subs'].append(temp)
                    main['subs'].append(sub)

            targets.append(main)
        return targets

    def loadCategories(self):
        # 创建需要爬取的种类的确认单
        catejories_file = os.path.join(os.getcwd(), 'categories.json')
        if not os.path.exists(catejories_file):
            categories = self.getCategories()
            with open(catejories_file, 'w', encoding='utf-8') as json_file:
                json_file.write(json.dumps(categories, indent=4))
        else:
            with open(catejories_file, 'r', encoding='utf-8') as json_file:
                categories = json.loads(json_file.read())

        # 将已经 爬取过的类别 删除掉
        res_category = []
        while len(categories):
            category = categories.pop()
            if 'stage' not in category:
                res_category.append(category)

        print('待爬取的大类目一共 {} 种'.format(len(res_category)))

        return res_category

    @staticmethod
    def verifyStorage(category, parent_path):
        # 判断当前的大类别是否已经进行了爬取，获取其存储路径
        if 'storage' in category:
            return category['storage']
        else:
            temp_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
            category_path = os.path.join(parent_path, temp_name)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
            return category_path

    def crawlTargets(self):
        self.login()
        self.browser.get('https://www.tmall.hk/')  # 天猫国际主页面
        time.sleep(2)

        # 创建存储结果的路径
        storage_path = os.path.join(os.getcwd(), 'result')
        if not os.path.exists(storage_path):
            os.makedirs(storage_path)

        categories = self.loadCategories()

        # 遍历需要进行爬取的种类的清单
        try:
            for index, category in enumerate(categories):
                # 声明 与当前一样的 category 对象，后续需要对其进行存储
                temp_category = category  # very important 为了实现断点续爬

                # 判断当前的大类别是否已经进行了爬取，获取其存储路径
                temp_category['storage'] = self.verifyStorage(category, storage_path)

                print('当前爬取的大类目是：『{}』, 其子类一共 {} 种'.format(category['name'], len(category['subs'])))

                # 当发生爬取错误的时候，替换原来的 category 里面对应位置的记录，以更新爬取进度
                try:
                    for _index, subcategory in enumerate(category['subs']):
                        # 声明 与当前一样的 subcategory 对象，后续需要对其进行存储
                        temp_subcategory = subcategory  # very important 为了实现断点续爬
                        # 判断当前的子类别是否已经进行了爬取，获取其存储路径
                        temp_subcategory['storage'] = self.verifyStorage(subcategory, temp_category['storage'])

                        if 'stage' in temp_subcategory:  # 如果当前这个子类已经爬取完了，那么就跳过
                            continue

                        print('当前爬取的子类目是：『{}』, 其子类一共 {} 种'.format(subcategory['name'], len(subcategory['subs'])))

                        # 确认 上次断点的时候在爬取的 项目的进度
                        try:
                            for __index, item in enumerate(subcategory['subs']):
                                # 声明 与当前一样的 item 对象，后续需要对其进行存储
                                temp_item = item  # very important 为了实现断点续爬
                                current_page = 1  # 当前爬取的页面
                                write_title = True  # 判断是否需要输入 csv 标题

                                if 'stage' in item:
                                    if item['stage'] == 'finish':  # 如果当前这个项目已经爬取完了，那么就跳过这项目
                                        continue
                                    else:
                                        current_page = int(item['stage'])

                                if 'file' in item:
                                    file_path = item['file']
                                    write_title = False
                                else:
                                    temp_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))
                                    file_path = os.path.join(temp_subcategory['storage'], '{}.csv'.format(temp_name))
                                temp_item['file'] = file_path

                                # 对每一个项目的爬取过程进行状态记录，记录爬取的页数
                                # 将最终结果替换之前的对应位置上的记录
                                try:
                                    # 输入名称的查询方法
                                    print('当前爬取的项目是：『{}』'.format(item['name']))
                                    self.search(item['name'])
                                    with open(file_path, 'w+') as records_file:
                                        # 如果是该文件的第一次输入，则录入 csv 的标题
                                        if write_title:
                                            title = ','.join(
                                                ['商品id', '商品大类', '商品子类', '商品种类', '商品标题', '商品价格', '商品月销量', '店名',
                                                 '详情页网址', ])
                                            records_file.write('{}\n'.format(title))

                                        page_total = int(self.getPageTotal())  # 获取 商品列表页 总页数
                                        if page_total > self.top_page:
                                            page_total = self.top_page
                                        page_count = 1
                                        while page_count < page_total:  # 遍历 前多少页的 商品列表页
                                            # 跳过之前已经爬取过的页面
                                            if page_count != current_page:
                                                self.slideDown()  # 执行 下拉动作
                                                self.nextPage()  # 执行 按下一页按钮 动作
                                                self.sliderVerification()  # 检测是否有 滑块验证
                                                page_count += 1
                                            else:
                                                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                                '#J_ItemList .product .product-iWrap')))  # 确认 当前商品列表页 的 全部商品 都 加载完成
                                                html = self.browser.page_source  # 获取 当前页面的 源代码
                                                doc = pq(html)  # pq模块 解析 网页源代码
                                                goods_items = doc('#J_ItemList .product').items()  # 获取 当前页 全部商品数据
                                                for _ in goods_items:  # 遍历 全部商品数据
                                                    goods_title = _.find('.productTitle').text().replace('\n',
                                                                                                         '')  # 获取 商品标题 并清洗
                                                    goods_sales_volume = _.find(
                                                        '.productStatus span').text()  # 获取 商品月销量 并清洗
                                                    goods_price = _.find('.productPrice').text().replace('¥\n',
                                                                                                         '')  # 获取 商品价格 并清洗
                                                    goods_shop = _.find('.productShop').text().replace('\n',
                                                                                                       '')  # 获取 店名 并清洗
                                                    goods_url = ''.join(['https:', _.find('.productImg').attr(
                                                        'href')])  # 获取 详情页网址 并在地址最前面加上 https:
                                                    goods_id = re.match('.*?id=?(\d+)&.*', goods_url).group(
                                                        1)  # 获取 商品id
                                                    record = ','.join(
                                                        [goods_id, category['name'], subcategory['name'], item['name'],
                                                         goods_title, str(goods_price), str(goods_sales_volume),
                                                         goods_shop, goods_url])
                                                    print(record)
                                                    records_file.write('{}\n'.format(record))

                                                self.slideDown()  # 执行 下拉动作
                                                self.nextPage()  # 执行 按下一页按钮 动作
                                                self.sliderVerification()  # 检测是否有 滑块验证
                                                page_count += 1
                                                current_page += 1
                                                temp_item['stage'] = page_count

                                            time.sleep(2)
                                        # 如果没有任何错误发生，并且遍历完成了 pages, 则记录该子类已经爬取完成
                                        temp_item['stage'] = 'finish'
                                except:
                                    traceback.print_exc()
                                    raise CrawlException
                                finally:
                                    temp_subcategory['subs'][__index] = temp_item
                            # 如果没有任何错误发生，并且遍历完成了 items, 则记录该子类已经爬取完成
                            temp_subcategory['stage'] = 'finish'
                        except CrawlException:
                            raise CrawlException
                        finally:
                            temp_category['subs'][_index] = temp_subcategory
                    # 如果没有任何错误发生，并且遍历完成了 subcategory, 则记录该大类已经爬取完成
                    temp_category['stage'] = 'finish'
                except CrawlException:
                    raise CrawlException
                finally:
                    categories[index] = temp_category
        except CrawlException:
            self.browser.quit()
        finally:
            catejories_file = os.path.join(os.getcwd(), 'categories.json')
            with open(catejories_file, 'w', encoding='utf-8') as json_file:
                json_file.write(json.dumps(categories, indent=4))
