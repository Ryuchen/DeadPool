<h1 style="align-content: center">Welcome to DeadPool</h1>
<p style="align-content: center">
  <img src="https://img.shields.io/badge/version-v0.2-red.svg?cacheSeconds=2592000"  alt="version"/>
  <img src="https://img.shields.io/badge/language-python3-blue.svg?cacheSeconds=2592000"  alt="language"/>
  <img src="https://img.shields.io/badge/platform-linux-blue.svg?cacheSeconds=2592000"  alt="platform"/>
  <a href="http://www.gnu.org/licenses/gpl-3.0.html">
    <img alt="License: GPL" src="https://img.shields.io/badge/License-GPL-yellow.svg"/>
  </a>
</p>

该项目是一个使用celery作为主体框架的爬虫应用，灵感源自于日常校园项目中。

### 🏠 [个人小栈](https://ryuchen.github.io/)

  > 如果你觉得这个项目不错，想要深入了解，可以关注上面的个人小栈，未来更新的说明会刊登在这里，并且会不定时分享部分内容和心得

### 📎 项目说明:

因为之前工作期间深入使用过 celery 作为 django web 的后台异步任务调度，但是深感 celery 的强大，并不单单只是局限在 django 的附带使用。之后想深入使用一下这个框架作为主框架构建一个项目，但是后续在网上没有搜索到关于 celery 的单独项目作为参考( 可能是我搜的姿势不对，毕竟身高不够，视线太低 =.= )。既然没能找到一个很好的介绍和使用 celery 的开源 demo ，那就自己来吧，毕竟身为程序员，最大的技能就是动手造重复的轮子，并且沉迷其中不可自拔。想法是有了，但是基于什么去构建这个项目？( >.< ? )，研究生阶段在搞知识图谱，那么知识的来源是最重要的，索性就使用这个构建个爬虫项目吧。鉴于上述原因，我构建了这个项目，希望能够帮助自己深入理解和熟练使用 celery 的强大功能。

### 🔥 设计特性:

- 构建完善的 proxy pool 和 cookie pool 基类，实现简单的实例作为参考，可以根据自己的需求创建新的实例
- 拥有异步和周期两种任务种类的基础类别，可以根据自己需求实现相应功能
- 集成了常见的一些反爬取机制的识别工具，具体内容参见 [plugins](https://github.com/ryuchen/DeadPool/master/blob/common/plugins)
- 兼顾了celery的集群化解决方案，能够在分布式的情况下，自适应分配节点任务 （TODO）
- 能够模拟真实用户在网页上的浏览动作，极大的降低了被反爬机制识别的概率 （TODO）
- 使用 celery 的 canvas 功能允许灵活性的配置数据流结构 （TODO）

### 👌 代码说明：

```
/
├── apps/   # 任务目录
    ├── asynch/   # 异步任务目录（也是该框架运行各种爬虫脚本的主目录）        
        ├── tasks/
            ├── task_tmall/    # example for Tmall 商品爬取目录（其他爬取任务跟该目录框架一致）
                ├── __init__.py    
                ├── __main__.py    # 该任务的主程序入口
                ├── crawler.py    # 单一爬取程序
                ├── middleware.py    # 爬取后的页面处理程序
                └── pipline.py    # 处理后的信息存储程序
            └── __init__.py
        ├── __init__.py
        └── base.py    # 异步任务的基类，继承了该基类才能被框架正确导入
    │── periodic/   # 定时任务目录（该框架的通用脚本目录）
        ├── tasks/  
            ├── task_cookie.py   # 周期性更新请求的cookie
            ├── task_proxy.py   # 周期性更新代理池中的IP地址
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
        └── jobs.yaml   # 任务加载配置（将jobs.d中的配置文件include进来后开启任务）
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