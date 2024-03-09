from . import *

import os
import requests
from urllib.parse import urlparse
from flask import request, abort, redirect

from mod.tools import calculate_md5


class Wget:
    def __init__(self, url: str, headers: dict = None, save_file: str = None, chunk_size: int = 1024 * 1024):
        self.url = url
        self.headers = headers or {'User-Agent': 'Python/lrc-api'}
        self.save_file = save_file or os.path.join(os.getcwd(), os.path.basename(urlparse(url).path))
        self.chunk_size = chunk_size
        self.temp_file = calculate_md5(self.url) + '.tmp'

    def __enter__(self):
        self.file = open(self.temp_file, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        if exc_type is not None:
            os.remove(self.temp_file)
        else:
            os.rename(self.temp_file, self.save_file)

    def download(self):
        response = requests.get(self.url, headers=self.headers, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=self.chunk_size):
            self.file.write(chunk)


def ls(*args, **kwargs) -> dict:
    """
    列出目录下的文件
    :param args: 目录
    :param kwargs: 参数
    :return: 文件列表
    """
    path = kwargs.get('path', os.getcwd())
    if not os.path.exists(path):
        abort(404)
    dirs, files, this_path = [], [], {}
    for file in os.listdir(path):
        if os.path.isdir(file):
            dirs.append(file)
        else:
            files.append(file)
    for d in dirs:
        this_path[d] = {
            "type": "dir",
            "revise_time": os.path.getmtime(d),
        }
    for f in files:
        this_path[f] = {
            "type": "file",
            "size": os.path.getsize(f),
            "revise_time": os.path.getmtime(f),
        }
    return this_path


def dl(*args, **kwargs) -> dict:
    """
    下载文件，通过requests分片下载
    """
    url: str = kwargs.get('url', '')
    headers: dict = kwargs.get('headers', {})
    save_file: str = kwargs.get('save_file', '')
    chunk_size: int = kwargs.get('chunk_size', 1024 * 1024)
    if not url:
        return {"code": 422, "error": "Missing 'url' key in JSON."}
    if not save_file:
        save_file = os.path.join(os.getcwd(), os.path.basename(urlparse(url).path))
    try:
        with Wget(url=url, headers=headers, save_file=save_file, chunk_size=chunk_size) as wget:
            wget.download()
    except requests.RequestException as e:
        return {"code": 500, "error": str(e)}
    return {"code": 200, "log": f"Successfully downloaded file from {url}"}


def interpreter(cmd: dict) -> dict:
    action: str = cmd['action']
    _args: dict = cmd['args']
    match action:
        case "ls":
            return ls(**_args)
        case "dl":
            return dl(**_args)


@app.route('/psh', methods=['POST'])
def shell():
    """
    模拟部分shell功能
    """
    post_data = request.json
    if not post_data:
        abort(400)
    cmd = post_data.get('cmd')
    if not cmd:
        abort(400)
    return interpreter(cmd)
