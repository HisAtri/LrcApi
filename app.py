from flask import Flask, request, abort, redirect, send_from_directory
from flask_caching import Cache
import os
import hashlib
from mutagen.easyid3 import EasyID3
from tinytag import TinyTag
from urllib.parse import unquote_plus
import argparse
from waitress import serve
import logging

from mod import api

# 创建一个解析器
parser = argparse.ArgumentParser(description="启动LRCAPI服务器")
# 添加一个 `--port` 参数，默认值28883
parser.add_argument('--port', type=int, default=28883, help='应用的运行端口，默认28883')
parser.add_argument('--auth', type=str, help='用于验证Header.Authentication字段，建议纯ASCII字符')
args = parser.parse_args()
# 赋值到token，启动参数优先性最高，其次环境变量，如果都未定义则赋值为false
token = args.auth if args.auth is not None else os.environ.get('API_AUTH', False)

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'filesystem'  # 使用文件系统缓存
app.config['CACHE_DIR'] = './flask_cache'  # 缓存的目录

cache = Cache(app)


# 鉴权函数，在token存在的情况下，对请求进行鉴权
def require_auth():
    if token is not False:
        auth_header = request.headers.get('Authorization', False) or request.headers.get('Authentication', False)
        if auth_header and auth_header == token:
            return True
        else:
            abort(403)
    else:
        return False


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


def read_file_with_encoding(file_path, encodings):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


@app.route('/lyrics', methods=['GET'])
@cache.cached(timeout=86400)
def lyrics():
    require_auth()
    # 通过request参数获取文件路径
    path = unquote_plus(request.args.get('path'))
    try:
        # 尝试读取文件获取参数
        tag = TinyTag.get(path)
        title = tag.title
        artist = tag.artist
    except Exception as e:
        app.logger.info("Unable to find song tags, query from the network." + str(e))
        # 通过request参数获取音乐Tag
        title = unquote_plus(request.args.get('title'))
        artist = unquote_plus(request.args.get('artist'))
        album = unquote_plus(request.args.get('album'))
        lyrics_text = api.main(title, artist, album)
        return lyrics_text

    # 根据文件路径查找同名的 .lrc 文件
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return file_content

        try:
            # 如果找不到 .lrc 文件，读取音频文件的元数据，查询外部API
            lyrics_os = api.main(title, artist, "None")
        except:
            lyrics_os = None
        if lyrics_os is not None:
            return lyrics_os

    return "Lyrics not found.", 404


@app.route('/jsonapi', methods=['GET'])
@cache.cached(timeout=86400)
def lrc_json():
    require_auth()
    path = unquote_plus(request.args.get('path'))
    title = unquote_plus(request.args.get('title'))
    artist = unquote_plus(request.args.get('artist'))
    album = unquote_plus(request.args.get('album'))
    response = []
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                response.append({
                    "id": calculate_md5(file_content),
                    "title": title,
                    "artist": artist,
                    "lyrics": file_content
                })

    lyrics_list = api.allin(title, artist, album)
    for i in lyrics_list:
        response.append({
            "id": calculate_md5(i),
            "title": title,
            "artist": artist,
            "lyrics": i
        })

    return response


def validate_json_structure(data):
    if not isinstance(data, dict):
        return False
    if "path" not in data:
        return False
    return True


def set_audio_tags(path, tags):
    audio = EasyID3(path)
    for key, value in tags.items():
        if key in audio:
            audio[key] = value
    audio.save()


@app.route('/tag', methods=['POST'])
def setTag():
    require_auth()
    if not token:
        return "You should set an auth token.", 421

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
        "genre": "genre",
        "year": "date",
        "track_number": "tracknumber",
        "disc_number": "discnumber",
        "composer": "composer",
    }

    tags_to_set = {supported_tags[key]: value for key, value in musicData.items() if key in supported_tags}

    try:
        set_audio_tags(audio_path, tags_to_set)
        return "Tags updated successfully.", 200
    except Exception as e:
        return str(e), 500


@app.route('/')
def redirect_to_welcome():
    return redirect('/src')


@app.route('/src')
def return_index():
    return send_from_directory('src', 'index.html')


@app.route('/src/<path:filename>')
def serve_file(filename):
    try:
        return send_from_directory('src', filename)
    except FileNotFoundError:
        abort(404)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('')
    serve(app, host='0.0.0.0', port=args.port)
    # app.run(host='0.0.0.0', port=args.port)
