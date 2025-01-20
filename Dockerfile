# 使用更小的基础镜像
FROM python:3.12.1-slim as builder

# 设置工作目录
WORKDIR /app

# 安装必要的编译依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装依赖到指定目录
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# 最终阶段
FROM python:3.12.1-slim

WORKDIR /app

# 只复制必要的Python包
COPY --from=builder /install /usr/local

# 复制应用代码
COPY . .

# 清理不必要的文件（如果有的话）
RUN rm -rf __pycache__ \
    && rm -rf *.pyc \
    && find . -type d -name __pycache__ -exec rm -r {} +

# 设置启动命令
CMD ["python", "/app/app.py"]
