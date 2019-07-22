### 简介

在使用Jumpserver的过程中，发现导入资产并不是特别方便，虽然官方提供了通过xls表格进行导入的功能，不过依然需要去手动或脚本生成这个xls文件。之前弄过自动生成xls文件的脚本，现在升级一下，省去生成xls文件这一步，直接执行脚本就可以进行资产的导入。主要使用JMS SDK以及RestAPI（官方的SDK文档有点太简洁了，所以部分使用的是RestAPI）

**注意：** 已知适配JMS Version
  - 1.5.1

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
```

- 获取token
```
curl -XPOST -d'username=admin,password=xxxxxxx' http:///yourjms.address/api/users/v1/token/
```

- 获取所有用户
```
curl -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -XGET http://yourjms.address/api/users/v1/users/
```

- 获取系统管理用户信息
```
curl -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -XGET http://yourjms.address/api/assets/v1/admin-user/?name={ops-root}
```

- 创建用户组
```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -d '{"id":"96ea1864-f920-4b97-b8ca-5714e8426ed7","is_discard": false,"discard_time": "","name":"YourGroupName","comment":"","created_by": "administrator","date_created":"2018-06-06 06:03:03 +0000","discard_time":"2018-06-11 06:03:03 +0000"}' 'http://yourjms.address/api/users/v1/groups/'
```

- 创建用户并加入组
```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' 'http://yourjms.address/api/users/v1/users/' -d '{"id": "7e9174ef-6c1c-440d-9c9e-499496aaea19","groups": ["96ea1864-f920-4b97-b8ca-5714e8426ed7"],"last_login": "2018-05-19 06:03:03 +0000","is_active": true,"date_joined": "2018-06-06 06:03:03 +0000","username": "YourUserName","name": "YourUserName","email": "[your@main.com](mailto:your@mail.com)","role": "Admin","avatar": null,"wechat": "","phone": "","otp_level": 0,"comment": "","is_first_login": true,"date_expired": "2088-05-19 06:03:03 +0000","created_by": "2018-05-19 06:03:03 +0000"}'
```

- 获取系统用户详细信息
```
curl -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -XGET http://yourjms.address/api/assets/v1/system-user/?name={ops-user}
```

- 获取目前已有的资产节点（返回list）
```
curl -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -XGET http://yourjms.address/api/assets/v1/nodes/
```

- 创建用户资产
```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' -d '{"id": "123a01b7-b21f-4623-b7b3-7f2715ee4321","ip": "10.0.0.1","hostname": "YourHostName","port": 22,"platform": "Linux","is_active": true,"public_ip": null,"created_by": null,"comment": "","admin_user": "872a01b7-b21f-4623-b7b3-7f2715ee4ed8", "nodes": ["7e9174ef-6c1c-440d-9c9e-499496aaea19"]}' 'http://192.168.188.84/api/assets/v1/assets/'
```

- 获取所有资产
```
curl -X GET --header 'Content-Type: application/json' --header 'Accept: application/json' -H 'Authorization: Bearer 95a497da37ed492fa113a12a3f4a81d1' 'http://yourjms.address/api/assets/v1/assets/'
```
