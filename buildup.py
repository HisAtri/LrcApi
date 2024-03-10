import subprocess
import platform
import sys
import codecs
import os

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

PLATFORM = platform.system()
ARCHITECTURE = platform.machine()
APP_NAME = "lrcapi"
APP_VERSION = "1.5.2"
PACK_NAME = f"{APP_NAME}-{APP_VERSION}-{PLATFORM}-{ARCHITECTURE}{'.exe' if PLATFORM == 'Windows' else ''}"

# 针对Alpine，安装objdump/gcc环境等
subprocess.run("apk add --no-cache gcc musl-dev jpeg-dev zlib-dev libjpeg", shell=True)
subprocess.run("apk add binutils", shell=True)
# 安装Pyinstaller及主程序依赖
subprocess.run("pip install -r requirements.txt", shell=True)
subprocess.run("pip install pyinstaller", shell=True)

# 打包
def generate_add_data_options(root_dir):
    options = []
    for root, dirs, files in os.walk(root_dir):
        if files:
            # 将目录路径转换为 PyInstaller 可接受的格式
            formatted_path = root.replace("\\", "/")
            separator = ";" if PLATFORM == "Windows" else ":"
            options.append(f'--add-data "{formatted_path}/*{separator}{formatted_path}/"')
    return " ".join(options)


options = generate_add_data_options("src")
command = f"pyinstaller -F -i logo.png {options} app.py -n {PACK_NAME}"
subprocess.run(command, shell=True)
