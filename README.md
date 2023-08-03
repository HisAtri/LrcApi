# LrcApi
A Flask API For StreamMusic

## 功能

支持酷狗API获取LRC歌词、支持缓存、支持指定端口

已经打包了Linux_x86的程序，直接启动即可

其它环境也可以安装依赖之后启动app.py

默认监听28883端口，API地址`0.0.0.0:28883/lyrics`

启动参数 `--port` 指定端口

可以Nginx反向代理，可以SSL

## 食用方法：

### 二进制文件：

上传至运行目录，`./PyLrcAPI --port 8080`
	
### Python源文件：
		
上传至运行目录，解压tar.gz
		
安装依赖：`pip install -r requirements.txt`
		
启动服务：`python3 app.py --port 8080`

### Linux_x86一键部署运行：

```bash
wget https://mirror.eh.cx/APP/lrcapi.sh -O lrcapi.sh && chmod +x lrcapi.sh && sudo bash lrcapi.sh
```

### Docker部署方式

```bash
docker run -d -p 28883:28883 -v /home/user/music:/music hisatri/lyricapi:v1.0
```

非常**不建议**使用Docker部署Navidrome以及LRCAPI，但是如果你非要这么做，我也提供了以下的教程：

如果你正在使用Navidrome Docker，请将 `/home/user/music:/music` 中的 `/home/user/music` 修改为你在Navidrome中映射的主机路径。

如果你正在使用Navidrome（真的有人会本地部署Navidrome了，然后用Docker部署这东西？），请将你的音乐文件目录映射到Docker内目录；例如如果你音乐存储的目录是`/www/path/music`，请将启动命令中的映射修改为 `/www/path/music:/www/path/music`

然后访问`http://0.0.0.0:28883/lyrics`，或者使用Nginx或Apache进行反向代理及部署SSL证书。
