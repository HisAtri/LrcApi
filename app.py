import hashlib
import logging
import os
from urllib.parse import unquote_plus

import shutil
import requests
from flask import Flask, request, abort, redirect, send_from_directory, Response, jsonify, render_template_string, \
    make_response
from flask_caching import Cache
from waitress import serve
import concurrent.futures

from mod import search, lrc, tags
from mod.auth import webui, cookie
from mod.auth.authentication import require_auth
from mod.args import GlobalArgs

args = GlobalArgs()
app = Flask(__name__)

# 缓存逻辑
cache_dir = './flask_cache'
try:
    # 尝试删除缓存文件夹
    shutil.rmtree(cache_dir)
except FileNotFoundError:
    pass
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

    # 获取计算结果的十六进制表示，并去掉开头的 "0x"
    md5_hex = md5_hash.hexdigest()
    md5_hex = md5_hex.lstrip("0x")

    return md5_hex


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
        lrc_in = tags.r_lrc(path)
        if type(lrc_in) == str and len(lrc_in) > 0:
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
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def lrc_json():
    match require_auth(request=request):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421
    if not bool(request.args):
        abort(404, "请携带参数访问")
    path = unquote_plus(request.args.get('path'))
    title = unquote_plus(request.args.get('title'))
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
            i = lrc.standard(i)
            response.append({
                "id": calculate_md5(i),
                "title": title,
                "artist": artist,
                "lyrics": i
            })
    return jsonify(response)


@app.route('/cover', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_api():
    req_args = {key: request.args.get(key) for key in request.args}
    # 构建目标URL
    target_url = 'http://8.138.108.84:28884/cover?' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    """# 跟踪重定向并获取最终URL
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


def validate_json_structure(data):
    if not isinstance(data, dict):
        return False
    if "path" not in data:
        return False
    return True


@app.route('/tag', methods=['POST'])
def setTag():
    match require_auth(request=request):
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
        "title": "title",
        "artist": "artist",
        "album": "album",
        "lyrics": "lyrics"
    }

    tags_to_set = {supported_tags[key]: value for key, value in musicData.items() if key in supported_tags}
    result = tags.w_file(audio_path, tags_to_set)
    if result == 0:
        return "OK", 200
    elif result == -1:
        return "Failed to write lyrics", 523
    elif result == -2:
        return "Failed to write tags", 524
    else:
        return "Unknown error", 525


@app.route('/')
def redirect_to_welcome():
    return redirect('/src')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('src', 'img/Logo_Design.svg')


@app.route('/src')
def return_index():
    return send_from_directory('src', 'index.html')


@app.route('/src/<path:filename>')
def serve_file(filename):
    try:
        return send_from_directory('src', filename)
    except FileNotFoundError:
        abort(404)


@app.route('/login')
def login_check():
    if require_auth(request=request) < 0 and args.auth:
        return render_template_string(webui.html_login())

    return redirect('/src')


@app.route('/login-api', methods=['POST'])
def login_api():
    data = request.get_json()
    if 'password' in data:
        pwd = data['password']
        if args.valid(pwd):
            logger.info("user login")
            response = make_response(jsonify(success=True))
            response.set_cookie('api_auth_token', cookie.set_cookie(pwd))
            return response

    return jsonify(success=False)


def main():
    serve(app, host=args.ip, port=args.port, threads=32, channel_timeout=30)
    # app.run(host='0.0.0.0', port=args.port)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('')
    logger.info("正在启动服务器")
    main()
