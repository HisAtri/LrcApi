<div align="center">
    <img alt="LOGO" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/LrcAPI-Text-Extra.png" width="313" height="400" />
</div>

# LrcApi

A Flask API For [StreamMusic](https://github.com/gitbobobo/StreamMusic)

![LrcApi](https://socialify.git.ci/HisAtri/LrcApi/image?description=1&font=Source%20Code%20Pro&forks=1&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Light)

<p align="center">
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10|3.11|3.12-blue.svg" alt=""></a>
    <a href="https://hub.docker.com/r/hisatri/lyricapi"><img src="https://img.shields.io/badge/Docker-Quick%20Start-0077ED.svg" alt=""></a>
    <br>
    <img src="https://img.shields.io/github/license/HisAtri/LrcApi?color=%23f280bf" alt="">
    <img src="https://img.shields.io/github/commit-activity/m/HisAtri/LrcApi?color=%23bf4215" alt="">
    <img src="https://img.shields.io/github/stars/HisAtri/LrcApi?style=social" alt="">
</p>

<div align="center">
    <a href="README.md">中文</a> | <a href="README_EN.md">English</a>
    <br>
    <a href="https://docs.lrc.cx/" target="_blank">查阅文档</a>
</div>

## 功能

支持酷狗/聚合API获取LRC歌词

支持text/json API

支持获取音乐/专辑/艺术家封面

默认监听28883端口，API地址 `http://0.0.0.0:28883/lyrics` ；新版API地址 `http://0.0.0.0:28883/jsonapi` ；封面API地址 `http://0.0.0.0:28883/cover` 。

### 启动参数

| 参数       | 类型  | 默认值   |
|----------|-----|-------|
| `--port` | int | 28883 |
| `--auth` | str |       |

`--auth`参数用于header鉴权，留空则跳过鉴权。验证header中的`Authorization`或`Authentication`字段。如果鉴权不符合，则返回403响应。

也可以使用环境变量`API_AUTH`定义，其优先性低于`--auth`参数，但是更容易在Docker中部署。`-e API_AUTH=自定义一个鉴权key`

## 使用方法

### 公开API

如果无法私有部署，可以先尝试使用公开API。注意：公开API通过酷狗等接口获取歌词，可能响应较慢且并不完全准确。

歌词API地址：`https://api.lrc.cx/lyrics`

封面API地址: `https://api.lrc.cx/cover`

### 二进制文件

上传至运行目录，`./lrcapi --port 8080 --auth 自定义一个鉴权key`

### Python源文件

拉取本项目；或者下载后上传至运行目录，解压tar.gz

安装依赖：`pip install -r requirements.txt`

启动服务：`python3 app.py --port 8080 --auth 自定义一个鉴权key`

### Docker部署方式

```bash
docker run -d \
    -p 28883:28883 \
    -v /home/user/music:/music \
    -e API_AUTH=自定义一个鉴权key \
    hisatri/lyricapi:latest
```

或者，请指定一个Tag（推荐）

```bash
docker run -d \
    -p 28883:28883 \
    -v /home/user/music:/music \
    -e API_AUTH=自定义一个鉴权key \
    hisatri/lyricapi:1.5.0
```

如果你正在使用Navidrome Docker，请将 `/home/user/music:/music` 中的 `/home/user/music` 修改为你在Navidrome中映射的主机路径；

换句话说，`-v` 参数与Navidrome保持一致即可。

如果你正在使用Navidrome，请将你的音乐文件目录映射到Docker内目录；例如如果你音乐存储的目录是`/www/path/music`，请将启动命令中的映射修改为 `/www/path/music:/www/path/music`

然后访问 `http://0.0.0.0:28883/lyrics` 或新版API `http://0.0.0.0:28883/jsonapi` 

图片API地址为 `http://0.0.0.0:28883/cover`

注意：图片返回目前采用反向代理策略，可能存在一定的上下行流量消耗和延迟。

支持使用Nginx或Apache进行反向代理与SSL。

## Tag修改接口

### 接口详情

- 请求方法：POST
- 请求路径：/tag
- 数据类型：application/json

### 支持格式

已测试：

- FLAC(flac)
- ID3v2(mp3)
- VorbisComment(ogg)

### 支持标签

- 标题：title
- 艺术家：artist
- 专辑：album
- 歌词：lyrics

### 状态码

- 200 成功
- 404 未找到文件
- 421 无权限
- 422 解析错误
- 5xx 执行出错

### 简易测试环境

```python
import requests
json_data = {
    "path": "/path/to/music/file",
    "title": "title",
    "artist": "artist",
    "album": "album",
    "lyrics": "lyrics"
}
url = 'http://127.0.0.1:28883/tag'
response = requests.post(url, json=json_data)
print(response.status_code)
print(response.text)
```

## 二次开发说明

本程序基于GPL-3.0开源许可证，您可以自由免费地使用、修改和分发本程序。在二次开发时，请遵守以下要求：
1. 在您的衍生作品中保留原始版权和许可声明。
2. 如果您对本程序进行了修改，请清楚地说明您的修改。
3. 在进行分发时，您需要提供完整的源代码，并以GPL-3.0许可证分发您的衍生作品。
4. 任何以本程序为基础的商业用途都需要遵守GPL-3.0许可证，并保持免费开放访问。
5. 除源代码外，本项目的其他部分（包括Logo、服务或标语等）并非由 GPL 3.0 协议开源。

请确保您详细了解GPL-3.0许可证的要求并遵守相关规定。

# 赞赏一下

微信

<img alt="reward" class="rounded" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/qrcode.png" width="512" height="512" />

[![Star History Chart](https://api.star-history.com/svg?repos=HisAtri/LrcApi&type=Date)](https://star-history.com/#HisAtri/LrcApi&Date)
