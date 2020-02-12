<h1 align="center">Welcome to DeadPool(死海)</h1>
<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0-blue.svg?cacheSeconds=2592000" />
  <img src="https://img.shields.io/badge/language-python3-blue.svg?cacheSeconds=2592000" />
  <img src="https://img.shields.io/badge/platform-macos-blue.svg?cacheSeconds=2592000" />
  <a href="http://www.gnu.org/licenses/gpl-3.0.html">
    <img alt="License: GPL" src="https://img.shields.io/badge/License-GPL-yellow.svg" target="_blank" />
  </a>
</p>

该项目是一个使用celery作为主体框架的爬虫应用，灵感源自于日常校园项目中。

### 🏠 [个人小栈](https://ryuchen.github.io/)

  > 如果你觉得这个项目不错，想要深入了解，可以关注上面的个人小栈，未来更新的说明会刊登在这里，并且会不定时分享部分内容和心得

### 📎 项目说明:

  > 因为之前工作期间深入使用过 celery 作为 django web 的后台异步任务调度，但是深感 celery 的强大，并不单单只是局限在 django 的附带使用。
  > 之后想深入使用一下这个框架作为主框架构建一个项目，但是后续在网上没有搜索到关于 celery 的单独项目作为参考( 可能是我搜的姿势不对，毕竟身高不够，视线太低 =.= )。
  > 既然没能找到一个很好的介绍和使用 celery 的开源 demo ，那就自己来吧，毕竟身为程序员，最大的技能就是动手造重复的轮子，并且沉迷其中不可自拔。
  > 想法是有了，但是基于什么去构建这个项目？( >.< ? )，研究生阶段在搞知识图谱，那么知识的来源是最重要的，索性就使用这个构建个爬虫项目吧。
  > 鉴于上述原因，我构建了这个项目，希望能够帮助自己深入理解和熟练使用 celery 的强大功能。

### 🔥 设计特性:

- 构建完善的 proxy pool 和 cookie pool 基类，实现简单的实例作为参考，可以根据自己的需求创建新的实例
- 拥有异步和周期两种任务种类的基础类别，可以根据自己需求实现相应功能
- 集成了常见的一些反爬取机制的识别工具，具体内容参见 [plugins](https://github.com/ryuchen/DeadPool/master/blob/common/plugins)
- 兼顾了celery的集群化解决方案，能够在分布式的情况下，自适应分配节点任务
- 能够模拟真实用户在网页上的浏览动作，极大的降低了被反爬机制识别的概率
- 使用 celery 的 canvas 功能允许灵活性的配置数据流结构


### 👌 待办清单：
 * [x] 初步完成了框架的构建，并且配置了相关的参数
 * [x] 兼容 python2 和 python3 (目前暂定是都兼容，python2 兼容与否后续视情况而定)
 * [x] 构建 Readme.md
 
    * [x] 完成 Readme.md 文档的初步框架构建
    * [ ] 补充完成 Readme.md 文档的 install 和 contribute 模块
    
 * [ ] 构建 celery workflow 的任务调度模块
 
### 📖 安装说明:

```shell

celery -A deadpool worker -l info

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