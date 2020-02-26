<h1 align="center">Welcome to DeadPool</h1>
<p align="center">
  <img src="https://img.shields.io/badge/version-v0.2-red.svg?cacheSeconds=2592000"  alt="version"/>
  <img src="https://img.shields.io/badge/language-python3-blue.svg?cacheSeconds=2592000"  alt="language"/>
  <img src="https://img.shields.io/badge/platform-linux-blue.svg?cacheSeconds=2592000"  alt="platform"/>
  <a href="http://www.gnu.org/licenses/gpl-3.0.html">
    <img alt="License: GPL" src="https://img.shields.io/badge/License-GPL-yellow.svg"/>
  </a>
</p>

该项目是一个使用celery作为主体框架的爬虫应用(希望后期能够写成大型的爬虫项目框架)，灵感源自目前在学校进行的知识图谱的科研项目，主要用于该项目的网上文本数据采集工作。

### 🏠 [个人小栈](https://ryuchen.github.io/)

  > 如果你觉得这个项目不错，想要深入了解，可以关注上面的个人小栈，未来更新的说明会刊登在这里，并且会不定时分享部分内容和心得

### 📎 项目说明:

* 因为之前工作期间深入使用过 celery 作为 django web 的后台异步任务调度，但是深感 celery 的强大，并不应该局限在 django 异步任务中附带使用。
* 于是想深入拓展一下该框架的使用，便想以celery作为主框架构建一个项目，但是后续在网上没有搜索到关于 celery 的单独项目作为参考( 可能是我搜的姿势不对，毕竟身高不够，视线太低 =.= )。
* 既然没能找到一个很好的介绍和使用 celery 的开源 demo ，那就自己来吧，毕竟身为程序员，最大的技能就是动手造重复的轮子，并且沉迷其中不可自拔。
* 目前研究生阶段在搞实验室中的知识图谱构建的相关工程，那么知识的来源是最重要的，索性就以此出发根据该项目构建一个能够爬取不同站点的高并发爬虫框架。

鉴于上述原因，我构建了这个项目，希望能够帮助自己深入理解和熟练使用 celery 的强大功能。

### 🔥 设计特性:

#### 任务模块的划分

---
爬虫任务

> 构建在 apps.asynch.tasks 目录下面，拥有完备的抽象实现逻辑，并且以配置文件的形式进行任务功能的声明

* 拥有两个样例程序（task_tmall）和（task_eastmoney）
* 每个任务包含四个主要部分
  * __main__.py 主爬虫的入口程序，根据配置文件构建代码执行逻辑
  * crawler.py 单个主体的爬虫程序利用 requests 请求页面进行预处理
  * middleware.py 接收 crawler.py 的输出结果，进行数据清洗和提取
  * pipeline.py 将清洗后的结果按照配置文件存储到指定地方
* 能够实现爬取过程的断点续爬功能（TODO）
  * sqlite.sql 数据脚本文件创建 sqlite3 小数据库作为爬取记录

```yaml
# 需要进行引入的类的名称
class: "TaskEastmoney"
# 任务所在的类别
module: "asynch"
# 配置
options:
  # 登录配置声明 
  login:
    enable: false
    nickname: 'nickname'
    username: 'username'
    password: 'password'
  # proxy 配置声明
  proxy: true
  # cookie 配置声明
  cookie: true
  # 启用的存储模块声明
  storage:
    module: "MongoStorage"
    collection: ""  # 模块启用为 “FileStorage” 时，该配置为 path
  # 爬取时的关键字
  keyword:
    - "大豆"
    - "玉米"
```

---

周期任务

> 构建在 apps.periodic.tasks 目录下面，利用celery的周期任务特性，完成周期性任务的执行

* 拥有两个样例程序（task_proxy）和（task_cookie）(TODO)
  * task_proxy 构建代理池，周期性检查代理池中任务的状态，维护最低标准的可用IP
  * task_cookie 构建cookie池，周期性检查当前cookie是否可用，维护最低标准的可用cookie
  
---

插件模块

> 构建在 common.plugins 集成了常见的反爬机制识别、人为操作模拟和存储系统支持

* 在 human 库下实现了:
  * 模拟人为浏览页面进行滑动的操作(slider.py)
  * 常规滑块识别人机识别的程序操作(verification.py) (TODO)
* 在 storage 库下实现了：
  * 爬取内容的本地磁盘文本形式存储的功能支持(filestorage.py)
  * 爬取内容的mongodb文本形式存储的功能支持(mongostorage.py)
  
---

其他模块

> 为了尽可能的拓展支持的平台和项目的灵活性，而加入的功能

* 根据运行平台自动加载相对应的chromediver文件
* 通过配置文件的include，动态支持任务加载和取消

```yaml

# 在jobs.yaml中通过以下方式进行任务的开启关闭

# Base Tasks Router Settings
# Task name
jobs:
  #
  # Proxy Pool Settings
  task_proxy: !include jobs.d/periodic.d/task_proxy.yaml
  #
  # Cookie Pool Settings
  # task_cookie: !include jobs.d/periodic.d/task_cookie.yaml
  #
  # Tmall Crawler Settings
  # task_tmall: !include jobs.d/async.d/task_tmall.yaml
  #
  # Eastmoney Crawler Settings
  task_eastmoney: !include jobs.d/async.d/task_eastmoney.yaml

```
  
### 👌 代码说明：

```
/
├── apps/   # 任务目录
    ├── asynch/   # 异步任务目录（也是该框架运行各种爬虫脚本的主目录）        
        ├── tasks/
            ├── task_tmall/    # example for Tmall 商品爬取目录（其他爬取任务跟该目录框架一致）
                ├── sqlite.sql    # 为了之后中断续爬做准备
                ├── __init__.py    # 该任务的主程序入口
                ├── __main__.py    # 该任务的主程序入口
                ├── crawler.py    # 单一爬取程序
                ├── middleware.py    # 爬取后的页面处理程序
                └── pipline.py    # 处理后的信息存储程序
            └── __init__.py
        ├── __init__.py
        └── base.py    # 异步任务的基类，继承了该基类才能被框架正确导入
    │── periodic/   # 定时任务目录（该框架的通用脚本目录）
        ├── tasks/  
            ├── task_cookie   # 周期性更新请求的cookie （TODO）
            ├── task_proxy   # 周期性更新代理池中的IP地址 （TODO）
            └── __init__.py
        ├── __init__.py
        └── base.py    # 定时任务的基类，继承了该基类才能被框架正确导入
├── bin/
    └── chromedriver.exe   # browser driver 驱动程序
├── common/   # 通用库
    ├── plugins/   # 通用解析插件库
        ├── human/   # 模拟真人操作的库
            ├── slider.py   # 模拟真人浏览页面操作
            ├── verification.py   # 反爬验证程序操作
            └── __init__.py
        ├── storage/   # 爬取结果存储的库
            ├── filestorage.py   # 文件形式本地存储
            ├── mongostorage.py   # mongodb存储
            └── __init__.py
        └── __init__.py
    ├── settings.py   # 配置
    ├── singleton.py   # 单例模式
    ├── sqlitedao.py   # sqlite3操作封装，用于爬取过程中的记录
    ├── timetrans.py   # 时间格式转换
    ├── exceptions.py   # 异常类封装
    └── __init__.py    
├── config/   # 配置目录
    └── jobs.d/   # 任务配置目录
        ├── async.d/
            └── task_tmall.yaml
        ├── periodic.d/
            ├── task_cookie.yaml
            └── task_proxy.yaml
        ├── config.yaml   # 通用配置
        └── jobs.yaml   # 任务加载配置（将 jobs.d 中的配置文件 include 进来后开启任务）
├── contrib/   # celery 核心库
    ├── elastic/   # elasticsearch（用于执行任务日志记录）
        ├── indices/   # elasticsearch index mapping 
            ├── rlogs.py   # 运行日志的 index mapping
            └── __init__.py
        ├── base.py   # elasticsearch 实例创建类
        └── __init__.py
    ├── mysql/   # mysql（用来暂存 IP proxy）
        ├── tables/    # mysql table mapping 
            ├── proxy.py   # IP proxy table mapping
            └── __init__.py
        ├── base.py
        └── __init__.py
    ├── redis/   # redis（celery 运行时的broker和backend）
        ├── base.py   # redis 实例创建类
        └── __init__.py
    └── __init__.py
├── deadpool/   # celery application 主目录
    ├── celery.py   # 程序主入口
    └── __init__.py
├── driver/   # broswer 驱动存放目录
    ├── chromedriver_linux64.zip
    ├── chromedriver_mac64.zip
    └── chromedriver_win32.zip
├── logs   # 运行日志
├── result   # filestorage 插件的默认结果存放目录（可以通过配置文件修改）
├── test   # 开发时候的测试脚本
└── utils/   # 工具库
    ├── driver.py   # 依据平台加载 browser 驱动
    ├── loader.py   # yaml文件的第三方Loader
    ├── network.py   # 主机网络信息脚本
    └── __init__.py
```

### 📖 使用说明:

开发环境
* Windows 10 (Version 2004) WSL2 Ubuntu-18.04
* 运行环境依赖 redis/mysql/mongodb/elasticsearch
* 选装 rabbitmq 和 kibana

#### 安装说明

```shell script

# 目前只在 windows 环境下使用过该项目，其他平台的待测试~~
# 安装环境依赖
pip install -r requirements.txt

```
- - -
#### 运行说明

```shell script

# 在一个 shell 中执行该脚本
# 启动项目
celery -A deadpool flower worker -l info -P eventlet -E

# 另一个 shell 中执行该脚本
celery -A deadpool shell

# 在出现的Python编辑窗口中输入如下命令调用任务
Python 3.7.6 (tags/v3.7.6:43364a7ae0, Dec 19 2019, 00:42:30) [MSC v.1916 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from celery.execute import send_task
>>> send_task('task_tmall')

```
- - -
#### 查看状态

```shell script

# 同时可以在 浏览器中检测任务运行状态
https://localhost:5555

```

### 👤 作者介绍:

Ryuchen ( 陈 浩 )

* Github: [https://github.com/Ryuchen](https://github.com/Ryuchen)
* Email: [chenhaom1993@hotmail.com](chenhaom1993@hotmail.com)
* QQ: 455480366
* 微信: Chen_laws

Nameplace ( 虚位以待 )

### 🤝 贡献源码:

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/Ryuchen/DeadPool/tree/master/common/plugins).

### ⭐ 渴望支持: 

如果你想继续观察 Deadpool 接下来的走向，请给我们一个 ⭐ 这是对于我们最大的鼓励。
此外，如果你觉得 Deadpool 对你有帮助，你可以赞助我们一杯咖啡，鼓励我们继续开发维护下去。

| **微信**                         | **支付宝**                           |
| ------------------------------- | ----------------------------------- |
|<p align="center">![扫码赞助](https://raw.githubusercontent.com/Ryuchen/Panda-Sandbox/master/docs/sponsor/wechat.jpg)</p>|<p align="center">![扫码赞助](https://raw.githubusercontent.com/Ryuchen/Panda-Sandbox/master/docs/sponsor/alipay.jpg)</p>|

### 📝 开源协议:

Copyright © 2019 [Ryuchen](https://github.com/Ryuchen).<br />
This project is [GPL](http://www.gnu.org/licenses/gpl-3.0.html) licensed.
请谨遵开源协议，谢谢使用！

***
[![Release](https://img.shields.io/github/release/Ryuchen/DeadPool?color=blue)](https://github.com/Ryuchen/DeadPool/releases) [![Contributors](https://img.shields.io/github/contributors/Ryuchen/DeadPool?color=blue)](https://github.com/Ryuchen/DeadPool/graphs/contributors) [![Last commit](https://img.shields.io/github/last-commit/Ryuchen/DeadPool?color=blue)](https://github.com/Ryuchen/DeadPool/commits/master)

_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_