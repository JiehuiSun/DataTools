# DataTools

#### DataTools是数据管理工具
点击查看 [安装文档] (http://blog.sunjiehui.com/article/14)
点击查看 [操作使用] (http://blog.sunjiehui.com/article/16)
##### 解决方案:
* 在线查询sql
* 导出不同数据格式的查询sql集(包括导出csv/xls)
* 支持跨库拼接
* 支持一次性任务/定时任务/间隔任务

##### 配置项:
* 数据库配置
* 需求描述配置
* 需求对应SQL配置
* 需求定时发送方式及发送人配置
* 导出字段配置

___

#### 环境
* Python 3.7+
* Pip 10+

---
#### 开发顺序与规划
* ~~创建项目~~ ~~已完成~~
* ~~基础框架 已完成~~
* ~~使用UWSGI并正常启动项目 已完成~~
* ~~嵌入Admin管理页面 已完成~~
* ~~支持templates并支持配置json(方便后期扩展前后的分离) 已完成~~
* ~~实现在线sql执行并结果集展示(暂时不做长链接) 已完成~~
    * ~~功能 已完成~~
    * 美化
* ~~实现不同数据格式的导出(json/xls/csv) 已完成~~
    * ~~导出xls 已完成~~
    * 导出json
    * 导出csv
* **实现任务计划并前台展示任务列表及操作 正在开发**
    * ~~实现sql逻辑(单sql/多sqlO2O/多sqlO2M/多sqlM2M) 已完成~~
    * ~~后台任务列表/创建 已完成~~
    * ~~前台任务列表 已完成~~
    * ~~前台任务详情 已完成~~
    * 前台任务导出
    * 前台任务执行
    * ~~前台开启任务 已完成~~
    * ~~前台关闭任务 已完成~~
    * ~~启动项目时检查任务是否开启 已完成~~
    * 美化
* 优化DB链接
* 扩展为多用户/组的组织体系

___

#### 数据库管理
##### 该项目使用alembic进行数据库的管理

* pip install alembic 进行安装
* 在项目目录下执行 alembic init migrations，此时项目目录会生成alembic.ini文件，在里面配置自己的mysql：sqlalchemy.url, 默认使用的sqlite，如果有了alembic.ini/migrations需手动删除一下。
* 修改migrations/env.py文件内容：target_metadata
* 此时执行：alembic revision --autogenerate -m "init"，这样就会在migrations/versions中生成数据库迁移文件
* 执行：alembic upgrade head，就会在你的数据库中生成表 注意：使用mysql时请先在你的mysql中创建相应的数据库
