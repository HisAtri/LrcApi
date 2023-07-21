import base64
from flask import Flask, request
import os
import glob
from tinytag import TinyTag
import requests
from urllib.parse import unquote_plus, urlencode
from flask_caching import Cache
import argparse

# 创建一个解析器
parser = argparse.ArgumentParser(description="启动LRCAPI服务器")
# 添加一个 `--port` 参数，默认值28883
parser.add_argument('--port', type=int, default=28883, help='应用的运行端口，默认28883')
args = parser.parse_args()

app = Flask(__name__)

app.config['CACHE_TYPE'] = 'filesystem'  # 使用文件系统缓存
app.config['CACHE_DIR'] = './flask_cache'  # 缓存的目录
cache = Cache(app)

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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',}
    # 第一层Json，要求获得Hash值
    response = requests.get(f'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={searcher}&page=1&pagesize=2&showtype=1', headers=headers)
    if response.status_code == 200:
        song_info = response.json()
        try:
            songhash = song_info["data"]["info"][0]["hash"]
        except:
            return None
        # 第二层Json，要求获取歌词ID和AccessKey
        response2 = requests.get(f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={songhash}&album_audio_id=", headers=headers)
        lyrics_info = response2.json()
        lyrics_id = lyrics_info["candidates"][0]["id"]
        lyrics_key = lyrics_info["candidates"][0]["accesskey"]
        # 第三层Json，要求获得并解码Base64
        response3 = requests.get(f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyrics_id}&accesskey={lyrics_key}&fmt=lrc&charset=utf8", headers=headers)
        lyrics_data = response3.json()
        lyrics_encode = lyrics_data["content"]
        lrc_text = base64.b64decode(lyrics_encode).decode('utf-8')
        return lrc_text

    return None

@app.route('/lyrics', methods=['GET'])
def lyrics():
    path = unquote_plus(request.args.get('path'))

    # 根据文件路径查找同名的 .lrc 文件
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return file_content

        # 如果找不到 .lrc 文件，读取音频文件的元数据，查询外部API
        tag = TinyTag.get(path)
        title = tag.title
        artist = tag.artist
        try:
            lyrics = get_lyrics_from_net(title, artist)
        except:
            pass
        if lyrics is not None:
            return lyrics

    return "Lyrics not found.", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port)
