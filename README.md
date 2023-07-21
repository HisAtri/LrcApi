# LrcApi
A Flask API For StreamMusic

## 功能

支持酷狗API获取LRC歌词、支持缓存、支持指定端口

已经打包了Linux_x86的程序，直接启动即可

其它环境也可以安装依赖之后启动app.py

默认监听28883端口，API地址0.0.0.0:28883/lyrics

启动参数 --port 指定端口

可以Nginx反向代理，可以SSL

## 食用方法：

### 二进制文件：

上传至运行目录，./PyLrcAPI --port 8080
	
### Python源文件：
		
上传至运行目录，解压tar.gz
		
安装依赖：pip install -r requirements.txt
		
启动服务：python3 app.py --port 8080

### Linux_x86一键部署运行：

```bash
wget https://mirror.eh.cx/APP/lrcapi.sh -O lrcapi.sh && chmod +x lrcapi.sh && sudo bash lrcapi.sh
```
