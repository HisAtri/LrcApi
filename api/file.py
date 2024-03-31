import hashlib

from mod.auth import webui
from mod.auth.authentication import require_auth
from . import *

import os
import requests
from urllib.parse import urlparse
from flask import request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename

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


@v1_bp.route("/file/download", methods=["POST"])
def file_api_download():
    match require_auth(request=request, permission="rwd"):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    data = request.json
    if not data:
        return {"error": "invalid request body", "code": 400}, 400
    url = data.get("url")
    headers = data.get("headers") or {"User-Agent": "Python/lrc-api"}
    save_file = data.get("save_file")
    chunk_size = data.get("chunk_size") or 1024 * 1024
    if not url or not save_file:
        return {"error": "missing required parameters", "code": 400}, 400
    if os.path.exists(save_file):
        return {"error": "file already exists", "code": 400}, 409
    try:
        with Wget(url, headers, save_file, chunk_size) as wget:
            wget.download()
        return {"code": 200}, 200
    except requests.RequestException as e:
        return {"error": str(e), "code": 500}, 500


@v1_bp.route('/file/upload', methods=['POST'])
def upload_file():
    match require_auth(request=request, permission="rwd"):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    if 'file' not in request.files:
        return {"error": "No file part in the request", "code": 400}, 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    directory = request.form.get('directory')
    chunk_size = int(request.form.get('chunk_size'))
    start_position = int(request.form.get('start_position'))
    chunk_hash = request.form.get('chunk_hash')

    # 检查文件名是否为空
    if filename == '':
        return {"error": "No selected file", "code": 400}, 400

    # 检查分片哈希是否匹配
    file_content = file.read()
    if hashlib.md5(file_content).hexdigest() != chunk_hash:
        return {"error": "Chunk hash does not match", "code": 400}, 400

    # 将文件指针移动到分片起始位置
    file.seek(start_position)

    # 将分片写入文件
    with open(os.path.join(directory, filename), 'ab') as f:
        f.write(file_content[:chunk_size])

    return {"code": 200}, 200


@v1_bp.route('/file/list', methods=['GET'])
def list_file():
    match require_auth(request=request, permission="rwd"):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    path = request.args.get('path', os.getcwd())
    row = request.args.get('row', 500)
    page = request.args.get('page', 1)
    if not os.path.exists(path):
        return {"error": "Path does not exist", "code": 400}, 400
    if not os.path.isdir(path):
        return {"error": "Path is not a directory", "code": 400}, 400
    data = {
        "page": [page, row],
        "FILES": []
    }
    for i in os.listdir(path):
        if os.path.isdir(os.path.join(path, i)):
            # 目录，获取目录大小（默认4096，不遍历），创建时间（Int时间戳），修改时间（Int时间戳），用户(例如 root)，权限(例如 755)
            data["FILES"].append({
                "type": "dir",
                "name": i,
                "size": 4096,
                "ctime": int(os.path.getctime(os.path.join(path, i))),
                "mtime": int(os.path.getmtime(os.path.join(path, i))),
                "user": os.stat(os.path.join(path, i)).st_uid,
                "permission": oct(os.stat(os.path.join(path, i)).st_mode)[-3:]
            })
        else:
            # 文件，获取文件大小，创建时间（Int时间戳），修改时间（Int时间戳），用户(例如 root)，权限(例如 755)
            data["FILES"].append({
                "type": "file",
                "name": i,
                "size": os.path.getsize(os.path.join(path, i)),
                "ctime": int(os.path.getctime(os.path.join(path, i))),
                "mtime": int(os.path.getmtime(os.path.join(path, i))),
                "user": os.stat(os.path.join(path, i)).st_uid,
                "permission": oct(os.stat(os.path.join(path, i)).st_mode)[-3:]
            })

    return {
        "code": 200,
        "data": {
            "page": data["page"],
            "files": data["FILES"][row * (page - 1):row * page]
        }
    }


"""
@app.route('/file', methods=['GET'])
def file():
    return send_from_directory(src_path, 'file.html')
"""
