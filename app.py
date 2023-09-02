import base64
import json
import random
from flask import Flask, request, abort, redirect, send_from_directory
import os
from mutagen.easyid3 import EasyID3
from tinytag import TinyTag
import requests
from urllib.parse import unquote_plus
from flask_caching import Cache
import argparse
from waitress import serve
import threading
import logging

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
            return
        else:
            abort(403)


def postapi(song_info):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', }
    post_list = []
    song_list = song_info["data"]["info"]
    for ch in song_list:
        ch_hash = ch["hash"]  # hash
        ch_songname = ch["songname"]  # 标题
        ch_singer = ch["singername"]  # 专辑名
        ch_album = ch["album_name"]  # 歌手名

        ch_response = requests.get(
            f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={ch_hash}&album_audio_id=",
            headers=headers)
        ch_info = ch_response.json()
        ch_id = ch_info["candidates"][0]["id"]
        ch_key = ch_info["candidates"][0]["accesskey"]
        ch_responset = requests.get(
            f"http://lyrics.kugou.com/download?ver=1&client=pc&id={ch_id}&accesskey={ch_key}&fmt=lrc&charset=utf8",
            headers=headers)
        try:
            ch_lyrics_json = ch_responset.json()
            ch_lyrics = ch_lyrics_json["content"]
            ch_dest = {
                "id": ch_id,
                "key": ch_key,
                "name": ch_songname,
                "album": ch_album,
                "singer": ch_singer,
                "lyrics": ch_lyrics
            }
            post_list.append(ch_dest)
        except:
            pass

    post_json = json.dumps(post_list)
    logging.info("POST DATA")
    post_response = requests.post('https://ttk.eh.cx/endpoint', json=post_json)
    logging.info("Status Code:" + str(post_response.status_code))


def read_file_with_encoding(file_path, encodings):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


@cache.memoize(timeout=86400)
def get_lyrics_from_net(title, artist):
    if title is None and artist is None:
        return None
    title = "" if title is None else title
    artist = "" if artist is None else artist
    searcher = title + artist

    # 使用歌曲名和作者名查询歌曲
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', }
    # 第一层Json，要求获得Hash值
    response = requests.get(
        f'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={searcher}&page=1&pagesize=2&showtype=1',
        headers=headers)
    if response.status_code == 200:
        song_info = response.json()
        try:
            songhash = song_info["data"]["info"][0]["hash"]
        except:
            return None
        # 提交
        thread = threading.Thread(target=postapi, args=(song_info,))
        thread.start()
        # postapi(song_info)

        # 第二层Json，要求获取歌词ID和AccessKey
        response2 = requests.get(
            f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={songhash}&album_audio_id=",
            headers=headers)
        lyrics_info = response2.json()
        lyrics_id = lyrics_info["candidates"][0]["id"]
        lyrics_key = lyrics_info["candidates"][0]["accesskey"]
        # 第三层Json，要求获得并解码Base64
        response3 = requests.get(
            f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyrics_id}&accesskey={lyrics_key}&fmt=lrc&charset=utf8",
            headers=headers)
        lyrics_data = response3.json()
        lyrics_encode = lyrics_data["content"]
        lrc_text = base64.b64decode(lyrics_encode).decode('utf-8')
        return lrc_text

    return None


@app.route('/lyrics', methods=['GET'])
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
        try:
            # 通过request参数获取音乐Tag
            title = unquote_plus(request.args.get('title'))
            artist = unquote_plus(request.args.get('artist'))
            lyrics_text = get_lyrics_from_net(title, artist)
            return lyrics_text
        except Exception as e:
            app.logger.error("Unable to get song tags." + str(e))
            title, artist = None, None

    # 根据文件路径查找同名的 .lrc 文件
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return file_content

        try:
            # 如果找不到 .lrc 文件，读取音频文件的元数据，查询外部API
            lyrics = get_lyrics_from_net(title, artist)
        except:
            lyrics = None
        if lyrics is not None:
            return lyrics

    return "Lyrics not found.", 404


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
    return redirect('/statu')


@app.route('/statu')
def welcome():
    return 'The server is running'


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
