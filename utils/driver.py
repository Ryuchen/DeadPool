#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-11:31
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : driver.py
# @Desc : 
# ==================================================

import os
import zipfile
import platform


def loader_driver():
    os_ = platform.system()

    driver_name = "chromedriver"
    if os_ == "Linux":
        unpack_driver = "chromedriver_linux64.zip"
    elif os_ == "Darwin":
        unpack_driver = "chromedriver_mac64.zip"
    else:
        unpack_driver = "chromedriver_win32.zip"
        driver_name = "chromedriver.exe"

    driver_path = os.path.join("..", "driver", unpack_driver)

    # Create a ZipFile Object and load sample.zip in it
    with zipfile.ZipFile(driver_path, 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        zipObj.extractall(os.path.join("..", "bin"))

    return os.path.abspath(os.path.join("..", "bin", driver_name))