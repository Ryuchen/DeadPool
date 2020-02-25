#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:53
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : slider
# @Desc : 
# ==================================================
import time
import random

from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait


def slider_view(browser):
    """
    模拟正常用户浏览网页的动作
    :param browser:
    :return:
    """
    view_second = random.randint(5, 10)
    for i in range(int(view_second / 0.1)):
        js = "var q=document.documentElement.scrollTop=" + str(300 + 200 * i)
        browser.execute_script(js)
        time.sleep(0.1)
    js = "var q=document.documentElement.scrollTop=100000"
    browser.execute_script(js)
    time.sleep(0.2)

def slider_verification(browser, element, button):
    # 每次翻页后 检测是否有 滑块验证
    try:
        slider_button = WebDriverWait(self.browser, 5, 0.5).until(EC.presence_of_element_located((By.ID, 'nc_1_n1z')))
        actions = ActionChains(browser)
        actions.click_and_hold(slider_button).perform()
        trace = [10, 320]
        for x in trace:
            actions.move_by_offset(xoffset=x, yoffset=random.randint(-3, 3)).perform()
            actions = ActionChains(browser)
        time.sleep(1)
        actions.release().perform()
    except:
        print('没有检测到滑块验证码')