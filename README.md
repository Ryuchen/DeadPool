<h1 align="center">Welcome to Deadpool(死海)</h1>
<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0-blue.svg?cacheSeconds=2592000" />
  <img src="https://img.shields.io/badge/language-python3-blue.svg?cacheSeconds=2592000" />
  <img src="https://img.shields.io/badge/platform-macos-blue.svg?cacheSeconds=2592000" />
  <a href="http://www.gnu.org/licenses/gpl-3.0.html">
    <img alt="License: GPL" src="https://img.shields.io/badge/License-GPL-yellow.svg" target="_blank" />
  </a>
</p>

### 🏠 [个人小栈](https://ryuchen.github.io/)

  > 未来更新的说明会刊登在这里，并且会不定时分享部分内容和心得

### 📎 项目说明:
  > 因为之前工作期间深入使用过 celery 作为 django web 的后台异步任务调度，但是深感 celery 的强大，并不能只是局限于 django 的附带使用。
  > 但是后续在网上没有搜索到关于 celery 的单独项目(可能是我搜的姿势不对，毕竟坐着搜，视线太低)，没有很好的介绍和使用 celery 的开源demo。
  > 鉴于上述原因，我构建了这个项目，希望能够帮助自己和大家深入熟悉和熟练使用 celery 的强大功能。

### 🔥 设计特性:

- 能够支持自定义构建异步和定时任务，通过数据库进行任务的管理
- 将集成算子化操作的页面，进行任务的调度进程划分
- 将运行的结果和日志保存到 elasticsearch 中，并能够根据 elasticsearch 日志进行任务重试动作
- 将支持多节点任务集群化调度和任务的集群分发


### 👌 待办清单：
 * [x] 初步完成了框架的构建，并且配置了相关的参数
 * [x] 兼容 python2 和 python3 (目前暂定是都兼容，python2 兼容与否后续视情况而定)
 * [x] 集成部分定时任务的测试脚本 (后续将会删除)
 * [x] 构建 Readme.md
 
    * [x] 完成 Readme.md 文档的初步框架构建
    * [ ] 补充完成 Readme.md 文档的 install 和 contribute 模块
    
 * [ ] 构建 celery workflow 的任务调度模块
 
### 📖 安装说明:

```python

```

### 👤 作者介绍:

Ryuchen ( 陈 浩 )

* Github: [https://github.com/Ryuchen](https://github.com/Ryuchen)
* Email: [chenhaom1993@hotmail.com](chenhaom1993@hotmail.com)
* QQ: 455480366
* 微信: Chen_laws

Nameplace ( 虚位以待 )

### 🤝 贡献源码:

Contributions, issues and feature requests are welcome!<br />Feel free to check [issues page](https://github.com/Ryuchen/Deadpool/issues).

### ⭐ 渴望支持: 

如果你想继续观察 Deadpool 接下来的走向，请给我们一个 ⭐ 这是对于我们最大的鼓励。
此外，如果你觉得 Deadpool 对你有帮助，你可以赞助我们一杯咖啡，鼓励我们继续开发维护下去。

| **微信**                         | **支付宝**                           |
| ------------------------------- | ----------------------------------- |
|<p align="center">![扫码赞助](https://github.com/Ryuchen/Panda-Sandbox/raw/master/sponsor/wechat.jpg)</p>|<p align="center">![扫码赞助](https://github.com/Ryuchen/Panda-Sandbox/raw/master/sponsor/alipay.jpg)</p>|

### 📝 开源协议:

Copyright © 2019 [Ryuchen](https://github.com/Ryuchen).<br />
This project is [GPL](http://www.gnu.org/licenses/gpl-3.0.html) licensed.
请谨遵开源协议，谢谢使用！

***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_