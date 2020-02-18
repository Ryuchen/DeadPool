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