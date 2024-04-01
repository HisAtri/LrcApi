import os
import subprocess


platforms = ['linux/amd64', 'linux/arm64/v8', 'linux/arm/v7', 'linux/386', 'windows/amd64']
base_image = 'python:3.11'

# 将此脚本所在的根目录（项目目录）挂载到容器的 /app 目录下
root_dir = os.path.dirname(os.path.abspath(__file__))
container_root_dir = '/app'

# 在容器内使用buildup.py脚本自动化完成依赖安装、打包等操作
command_in_docker = "python /app/buildup.py"

for platform in platforms:
    # 使用docker run命令在不同平台的容器中执行打包命令
    command = f"docker run --rm -v {root_dir}:{container_root_dir} --platform {platform} {base_image} {command_in_docker}"
    subprocess.run(command, shell=True)
