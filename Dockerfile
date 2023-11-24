# 基于Python3.9 alpine镜像
FROM python:3.9.17-alpine3.18

# 设置工作目录
WORKDIR /app

# 将源代码复制到Docker镜像中
COPY ./LrcApi /app

# 安装Python项目依赖
RUN pip install -r /app/requirements.txt

# 设置启动命令
CMD ["python", "/app/app.py"]