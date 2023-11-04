# LrcApi

A Flask API For [StreamMusic](https://github.com/gitbobobo/StreamMusic)

## 功能

支持酷狗/咪咕/聚合API获取LRC歌词、支持缓存、支持指定端口

已经打包了Linux_x86的程序，直接启动即可

其它环境也可以安装依赖之后启动app.py

默认监听28883端口，API地址 `http://0.0.0.0:28883/lyrics` ；新版API地址 `http://0.0.0.0:28883/jsonapi`

支持修改MusicTag(实验性功能)

### 启动参数

|   参数   |   类型  | 默认值 |
| -------- | -------- | -------- |
| `--port`   | int   | 28883   |
| `--auth`  | str   |     |

`--auth`参数用于header鉴权，留空则跳过鉴权。验证header中的`Authorization`或`Authentication`字段。如果鉴权不符合，则返回403响应。

也可以使用环境变量`API_AUTH`定义，其优先性低于`--auth`参数，但是更容易在Docker中部署。`-e API_AUTH=DbG91ZEZbBgNVBAs`

## 食用方法

### 公开API

如果无法私有部署，可以先尝试使用公开API。注意：公开API通过酷狗接口获取歌词，可能并不完全准确。

API地址：`https://lrc.xms.mx/lyrics`

### 二进制文件

上传至运行目录，`./lrcapi --port 8080 --auth DbG91ZEZbBgNVBAs`

### Python源文件

拉取本项目；或者下载后上传至运行目录，解压tar.gz

安装依赖：`pip install -r requirements.txt`

启动服务：`python3 app.py --port 8080 --auth DbG91ZEZbBgNVBAs`

### Linux_x86一键部署运行

```bash
wget https://mirror.eh.cx/lrcapi/lrcapi.sh -O lrcapi.sh && chmod +x lrcapi.sh && sudo bash lrcapi.sh
```

### Docker部署方式

```bash
docker run -d -p 28883:28883 -v /home/user/music:/music hisatri/lyricapi:latest
```

或者，请指定一个Tag（推荐）

```bash
docker run -d -p 28883:28883 -v /home/user/music:/music hisatri/lyricapi:alpine-py1.3.4
```

如果你正在使用Navidrome Docker，请将 `/home/user/music:/music` 中的 `/home/user/music` 修改为你在Navidrome中映射的主机路径。

如果你正在使用Navidrome（真的有人会本地部署Navidrome了，然后用Docker部署这东西？），请将你的音乐文件目录映射到Docker内目录；例如如果你音乐存储的目录是`/www/path/music`，请将启动命令中的映射修改为 `/www/path/music:/www/path/music`

然后访问 `http://0.0.0.0:28883/lyrics` 或新版API `http://0.0.0.0:28883/jsonapi` 

支持使用Nginx或Apache进行反向代理与SSL。

## 常见状态码及可能含义

|   状态码   |   含义   |
|-----------|----------|
| 200 | 成功处理并返回结果 |
| 403 | Auth token不正确，拒绝响应|
| 404 | 未找到结果 |
| 421 | 你需要设置Auth token，才能访问这个服务 |
| 422 | 传入的数据格式不正确 |
| 503 | 服务器处理过程出现错误，具体查看日志 |

## MusicTag API

**此功能尚在测试中**，接收一段POST JSON文本，可修改指定音频文件

JSON应当包含文件路径`path`，以及要修改的Tag

由于该功能会修改文件内容，因此`auth`参数是必须的，否则会拒绝并返回`421`状态码，可以通过启动参数`--auth`或环境变量`API_AUTH`定义，详见上文说明。

### 支持的标签

用户可以在请求的JSON中提供以下标签字段来编辑音频文件的标签：

- "title": 音频文件的标题或名称。
- "artist": 音频文件的作者/艺术家。
- "album": 音频文件所属的专辑。
- "genre": 音频文件的流派。
- "year": 音频文件的发行年份。
- "track_number": 音频文件在专辑中的曲目号。
- "disc_number": 音频文件在多碟专辑中的碟片号。
- "composer": 音频文件的作曲家。

另外，如果在JSON中只定义了部分标签，例如只定义了"title"字段，程序会按照用户提供的字段进行标签编辑，只修改已经提供的标签，而保持其他标签不变。

### 示例JSON

```json
{
    "path": "/path/to/your/audio/file.mp3",
    "title": "The Music",
    "artist": "The Artist",
    "album": "Greatest Hits",
    "genre": "Rock",
    "year": "2022",
    "track_number": "3",
    "disc_number": "1",
    "composer": "Talented Composer"
}
```

### Python Demo

```python
import requests

# 定义API端点和鉴权令牌
api_url = 'https://api.example.com/tag'
auth_token = 'your_auth_token'

json_data = {
    "path": "/path/to/your/audio/file.mp3",
    "title": "New Title",
    "artist": "Awesome Artist"
}

headers = {
    "Content-Type": "application/json",
    "Authentication": auth_token
}

response = requests.post(api_url, json=json_data, headers=headers)

# 解析响应
if response.status_code == 200:
    print("Tags updated successfully.")
else:
    print("Error:", response.text)
```

## 二次开发说明

本程序基于GPL-3.0开源许可证，您可以自由使用、修改和分发本程序。在二次开发时，请遵守以下要求：
1. 在您的衍生作品中保留原始版权和许可声明。
2. 如果您对本程序进行了修改，请清楚地说明您的修改。
3. 在进行分发时，您需要提供完整的源代码，并以GPL-3.0许可证分发您的衍生作品。
4. 任何以本程序为基础的商业用途都需要遵守GPL-3.0许可证，并保持免费开放访问。

请确保您详细了解GPL-3.0许可证的要求并遵守相关规定。

# 赞赏一下

爱发电地址 <https://afdian.net/a/hisatri>
