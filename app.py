import os
import shutil
import hashlib
import logging
import sys

import requests
import concurrent.futures

from flask import Flask, Blueprint, request, abort, redirect, send_from_directory, jsonify, render_template_string, \
    make_response
from flask_caching import Cache
from waitress import serve
from urllib.parse import unquote_plus

from mod import search, lrc
from mod import tag
from mod import run_process
from mod.auth import webui, cookie
from mod.auth.authentication import require_auth
from mod.args import GlobalArgs

args = GlobalArgs()
app = Flask(__name__)

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')

# Blueprint直接复制app配置项
v1_bp.config = app.config.copy()

# 缓存逻辑
cache_dir = './flask_cache'
try:
    # 尝试删除缓存文件夹
    shutil.rmtree(cache_dir)
except FileNotFoundError:
    pass
# 定义缓存逻辑为本地文件缓存，目录为cache_dir = './flask_cache'
cache = Cache(app, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': cache_dir
})


# 缓存键，解决缓存未忽略参数的情况
def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args


# hash计算器
def calculate_md5(string):
    # 创建一个 md5 对象
    md5_hash = hashlib.md5()

    # 将字符串转换为字节流并进行 MD5 计算
    md5_hash.update(string.encode('utf-8'))

    # 获取计算结果的十六进制表示
    md5_bytes = md5_hash.digest()
    md5_str = md5_bytes.hex()

    return md5_str


# 跟踪重定向
def follow_redirects(url, max_redirects=10):
    for _ in range(max_redirects):
        response = requests.head(url, allow_redirects=False)
        if response.status_code == 200:
            return url
        elif 300 <= response.status_code < 400:
            url = response.headers['Location']
        else:
            abort(404)  # 或者根据需求选择其他状态码
    abort(404)  # 达到最大重定向次数仍未获得 200 状态码，放弃


def read_file_with_encoding(file_path, encodings):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


@app.route('/lyrics', methods=['GET'])
@v1_bp.route('/lyrics/single', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def lyrics():
    match require_auth(request=request):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    # 通过request参数获取文件路径
    if not bool(request.args):
        abort(404, "请携带参数访问")
    path = unquote_plus(request.args.get('path', ''))
    # 根据文件路径查找同名的 .lrc 文件
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return lrc.standard(file_content)
    try:
        lrc_in = tag.tout(path).get("lyrics", "")
        if type(lrc_in) is str and len(lrc_in) > 0:
            return lrc_in
    except:
        pass
    try:
        # 通过request参数获取音乐Tag
        title = unquote_plus(request.args.get('title'))
        artist = unquote_plus(request.args.get('artist', ''))
        album = unquote_plus(request.args.get('album', ''))
        executor = concurrent.futures.ThreadPoolExecutor()
        # 提交任务到线程池，并设置超时时间
        future = executor.submit(search.main, title, artist, album)
        lyrics_text = future.result(timeout=30)
        return lrc.standard(lyrics_text)
    except:
        return "Lyrics not found.", 404


@app.route('/jsonapi', methods=['GET'])
@v1_bp.route('/lyrics/advance', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def lrc_json():
    match require_auth(request=request):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    if not bool(request.args):
        abort(404, "请携带参数访问")
    path = unquote_plus(request.args.get('path', ''))
    title = unquote_plus(request.args.get('title', ''))
    artist = unquote_plus(request.args.get('artist', ''))
    album = unquote_plus(request.args.get('album', ''))
    response = []
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                file_content = lrc.standard(file_content)
                response.append({
                    "id": calculate_md5(file_content),
                    "title": title,
                    "artist": artist,
                    "lyrics": file_content
                })

    lyrics_list = search.allin(title, artist, album)
    if lyrics_list:
        for i in lyrics_list:
            if not i:
                continue
            i = lrc.standard(i)
            response.append({
                "id": calculate_md5(i),
                "title": title,
                "artist": artist,
                "lyrics": i
            })
    _response = jsonify(response)
    _response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return jsonify(response)


@app.route('/cover', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_api():
    req_args = {key: request.args.get(key) for key in request.args}
    # 构建目标URL
    target_url = 'http://api.lrc.cx/cover?' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    """
    # 跟踪重定向并获取最终URL
    final_url = follow_redirects(target_url)
    # 获取最终URL的内容或响应
    response = requests.get(final_url)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        return Response(response.content, content_type=content_type)
    else:
        abort(404)
    """
    return redirect(target_url, 302)


@v1_bp.route('/cover/<path:s_type>', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_new(s_type):
    __endpoints__ = ["music", "album", "artist"]
    if s_type not in __endpoints__:
        abort(404)
    req_args = {key: request.args.get(key) for key in request.args}
    target_url = f'http://api.lrc.cx/cover/{s_type}/' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    return redirect(target_url, 302)


@app.route('/tag', methods=['GET', 'POST', 'PUT'])
@v1_bp.route('/tag', methods=['GET', 'POST', 'PUT'])
def setTag():
    def validate_json_structure(data):
        if not isinstance(data, dict):
            return False
        if "path" not in data:
            return False
        return True

    match require_auth(request=request, permission='rw'):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421

    musicData = request.json
    if not validate_json_structure(musicData):
        return "Invalid JSON structure.", 422

    audio_path = musicData.get("path")
    if not audio_path:
        return "Missing 'path' key in JSON.", 422

    if not os.path.exists(audio_path):
        return "File not found.", 404

    supported_tags = {
        "tracktitle": {"allow": (str, bool, type(None)), "caption": "Track Title"},
        "artist": {"allow": (str, bool, type(None)), "caption": "Artists"},
        "album": {"allow": (str, bool, type(None)), "caption": "Albums"},
        "year": {"allow": (int, bool, type(None)), "caption": "Album year"},
        "lyrics": {"allow": (str, bool, type(None)), "caption": "Lyrics text"}
    }
    if "title" in musicData and "tracktitle" not in musicData:
        musicData["tracktitle"] = musicData["title"]
    tags_to_set = {}
    for key, value in musicData.items():
        if key in supported_tags and isinstance(value, supported_tags[key]["allow"]):
            tags_to_set[key] = value
    try:
        tag.tin(tags=tags_to_set, file=audio_path)
    except TypeError as e:
        return str(e), 524
    except FileNotFoundError as e:
        return str(e), 404
    except Exception as e:
        return str(e), 500
    return "Succeed", 200


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
    return send_from_directory('src', 'img/Logo_Design.svg')


@app.route('/src')
def return_index():
    """
    显示主页
    :return: index page
    """
    return send_from_directory('src', 'index.html')


@app.route('/src/<path:filename>')
def serve_file(filename):
    """
    路由/src/
    路径下的静态资源
    :param filename:
    :return:
    """
    FORBIDDEN_EXTENSIONS = ('.exe', '.bat', '.dll', '.sh', '.so', '.php', '.sql', '.db', '.mdb', '.gz', '.tar', '.bak',
                            '.tmp', '.key', '.pem', '.crt', '.csr', '.log')
    if filename.lower().endswith(FORBIDDEN_EXTENSIONS):
        abort(404)
    try:
        return send_from_directory('src', filename)
    except FileNotFoundError:
        abort(404)


@app.route('/file/<path:filename>')
@v1_bp.route('/file/<path:filename>')
def file_viewer(filename):
    """
    文件查看器
    :param filename:
    :return:
    """
    # 需要权限
    match require_auth(request=request):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    # 拓展名白名单
    ALLOWED_EXTENSIONS = ('.mp3', '.flac', '.wav', '.ape', '.ogg', '.m4a', '.aac', '.wma', '.mp4', '.m4p', '.m4b',
                          'txt', 'lrc', 'webp', 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'svg', 'ico', 'mp4', 'webm',
                          'mkv', 'avi', 'mov', 'wmv', 'flv', 'f4v', 'f4p', 'f4a', 'f4b', 'm4v', 'm4r', 'm4p', 'm4b',)
    if filename.lower().endswith(ALLOWED_EXTENSIONS):
        try:
            return send_from_directory(os.path.dirname(filename), os.path.basename(filename))
        except FileNotFoundError:
            abort(404)


@app.route('/login')
def login_check():
    """
    登录页面
    未登录时返回页面，已登录时重定向至主页
    :return:
    """
    if require_auth(request=request) < 0 and args.auth:
        return render_template_string(webui.html_login())

    return redirect('/src')


@app.route('/login-api', methods=['POST'])
def login_api():
    """
    登录对接的API
    包括验证和下发Cookie
    success提示成功与否
    :return:
    """
    data = request.get_json()
    if 'password' in data:
        pwd = data['password']
        if args.valid(pwd):
            logger.info("user login")
            response = make_response(jsonify(success=True))
            response.set_cookie('api_auth_token', cookie.set_cookie(pwd))
            return response

    return jsonify(success=False)


def main(debug=False):
    if not debug:
        # Waitress WSGI 服务器
        serve(app, host=args.ip, port=args.port, threads=32, channel_timeout=30)
        # Debug服务器
        # app.run(host='0.0.0.0', port=args.port)
    else:
        logger.info("程序将以Debug模式启动")
        app.run(host='0.0.0.0', port=args.port, debug=True)


if __name__ == '__main__':
    # 对Python版本进行检查（要求Python 3.10+）
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ required, but you are using Python {}.{}.{}.".format(*sys.version_info[:3]))

    # 日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('')
    logger.info("正在启动服务器")
    run_process.run()
    # 注册 Blueprint 到 Flask 应用
    app.register_blueprint(v1_bp)
    # 启动
    main(args.debug)
