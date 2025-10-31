# 说明

参考[原repo](https://github.com/HisAtri/LrcApi)


# 新增特点

1. 使海外ip能正常使用
2. 用docker compose进行管理


# 用法

1. 复制docker compose配置文件
```
cp docker-compose.yml.example docker-compose.yml
```

2. 修改*docker-compose.yml*中的设置

- 必须增加音乐文件路径。将第10行的`/path/to/your/music`，替换成自己的音乐文件夹路径
- 必须设置验证字符串`API_AUTH`

具体可以参考*app/README*

3. 启动docker

初次启动会编译镜像，大概需要几十秒到几分钟。
```
docker compose up -d
```

4. 确认运行状态
```
docker compose ps
```
