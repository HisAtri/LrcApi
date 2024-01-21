# 第一阶段：安装GCC
FROM python:3.12.1-alpine as gcc_installer

# 安装GCC
RUN apk add --no-cache gcc musl-dev

# 第二阶段：安装Python依赖
FROM gcc_installer as requirements_installer

# 设置工作目录
WORKDIR /app

# 只复制 requirements.txt，充分利用 Docker 缓存层
COPY ./LrcApi/requirements.txt /app/

# 安装Python依赖
RUN pip install --no-user --prefix=/install -r requirements.txt

# 第三阶段：运行环境
FROM python:3.12.1-alpine

# 设置工作目录
WORKDIR /app

# 复制Python依赖
COPY --from=requirements_installer /install /usr/local

# 复制项目代码
COPY ./LrcApi /app

# 设置启动命令
CMD ["python", "/app/app.py"]
