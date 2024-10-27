from . import *

import os

from flask import abort, redirect, send_from_directory

from mod.auth import require_auth_decorator


@app.route('/')
def redirect_to_welcome():
    """
    重定向至/src，显示主页
    :return:
    """
    return redirect('/src')


@app.route('/favicon.ico')
def favicon():
    """
    favicon位置，返回图片
    :return:
    """
    return send_from_directory(src_path, 'img/Logo_Design.svg')


@app.route('/src')
def return_index():
    """
    显示主页
    :return: index page
    """
    return send_from_directory(src_path, 'index.html')


@app.route('/src/<path:filename>')
def serve_file(filename):
    """
    路由/src/
    路径下的静态资源
    :param filename:
    :return:
    """
    FORBIDDEN_EXTENSIONS = ('.exe', '.bat', '.dll', '.sh', '.so', '.php', '.sql', '.db', '.mdb', '.gz', '.tar', '.bak',
                            '.tmp', '.key', '.pem', '.crt', '.csr', '.log', '.html', '.htm', '.xml', '.json', '.yml',)
    _paths = filename.split('/')
    for _path in _paths:
        if _path.startswith('.'):
            abort(404)
    if filename.lower().endswith(FORBIDDEN_EXTENSIONS):
        abort(404)
    try:
        return send_from_directory(src_path, filename)
    except FileNotFoundError:
        abort(404)


@app.route('/file/<path:filename>')
@v1_bp.route('/file/<path:filename>')
@require_auth_decorator(permission='r')
def file_viewer(filename):
    """
    文件查看器
    :param filename:
    :return:
    """
    # 拓展名白名单
    ALLOWED_EXTENSIONS = ('.mp3', '.flac', '.wav', '.ape', '.ogg', '.m4a', '.aac', '.wma', '.mp4', '.m4p', '.m4b',
                          'txt', 'lrc', 'webp', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'svg', 'ico', 'mp4', 'webm',
                          'mkv', 'avi', 'mov', 'wmv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'm4v', 'm4r', 'm4p', 'm4b',)
    if filename.lower().endswith(ALLOWED_EXTENSIONS):
        try:
            return send_from_directory(os.path.dirname(filename), os.path.basename(filename))
        except FileNotFoundError:
            abort(404)
