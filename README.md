### 简介

在使用Jumpserver的过程中，发现导入资产并不是特别方便，虽然官方提供了通过xls表格进行导入的功能，不过依然需要去手动或脚本生成这个xls文件。之前弄过自动生成xls文件的脚本，现在升级一下，省去生成xls文件这一步，直接执行脚本就可以进行资产的导入。主要使用JMS SDK以及RestAPI（官方的SDK文档有点太简洁了，所以部分使用的是RestAPI）

**注意：** 已知适配JMS Version
  - 1.5.0/1.5.1
  - 1.4.8

执行环境:`python 3.6.4`

目前完成度
- [x] 支持网域
- [x] 支持AWS资产导入
- [x] 支持Aliyun资产导入
- [x] 支持根据主机特定信息更新资产描述（适合终端快速查找并连接）
- [x] 支持自动创建资产节点并根据需要添加资产



### 使用方法

- 下载脚本
```
git clone git@github.com:Gourds/jms-assets-import.git
```


- 使用
修改配置文件，直接执行就可以了


### 可能对你有帮助（RestAPI）

- API文档
```
http://your_jms_host:port/api/assets/v1/nodes/
https://docs.jumpserver.org/zh/docs/api_style_guide.html
```

- 数据格式，根据需要参考API确定需要哪些key
```
{
	'hostname': 'xxx',
	'id': 'xxx-xxx-xxx-xxx',
	'ip': '1.1.1.1',
	'is_actice': 'true',
	'comment': '[xxx]',
	'nodes': ['xxx-xxx-xxx-xxx', 'xxx-xxx-xxx-xxx'],
	'domain': 'xxx-xxx-xxx-xxx',
	'admin_user': 'xxx-xxx-xxx-xxx',
	'protocols': ['ssh/22']
}
```
