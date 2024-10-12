from . import *

import os

from flask import request, abort, jsonify, render_template_string
from urllib.parse import unquote_plus

from mod import lrc
from mod import searchx
from mod import tools
from mod import tag
from mod.auth import webui
from mod.auth.authentication import require_auth


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
    if path and os.path.isfile(path):
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return lrc.standard(file_content)
    try:
        lrc_in = tag.read(path).get("lyrics", "")
        if type(lrc_in) is str and len(lrc_in) > 0:
            return lrc_in
    except:
        pass
    try:
        # 通过request参数获取音乐Tag
        title = unquote_plus(request.args.get('title'))
        artist = unquote_plus(request.args.get('artist', ''))
        album = unquote_plus(request.args.get('album', ''))
        result: list = searchx.search_all(
            title=title, artist=artist, album=album, timeout=30)
        if not result[0].get('lyrics'):
            return "Lyrics not found.", 404

        # 如果音乐文件存在, 则保存对应的歌词到本地
        if path and os.path.isfile(path):
            lrc_path = os.path.splitext(path)[0] + '.lrc'
            if os.path.isfile(lrc_path):
                with open(lrc_path, "w") as file:
                    file.write(result[0].get('lyrics'))

        return result[0].get('lyrics')
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
    if path and os.path.isfile(path):
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                file_content = lrc.standard(file_content)
                response.append({
                    "id": tools.calculate_md5(file_content),
                    "title": title,
                    "artist": artist,
                    "lyrics": file_content
                })

    lyrics_list = searchx.search_all(title, artist, album)
    if lyrics_list:
        for i in lyrics_list:
            if not i:
                continue
            i['lyrics'] = lrc.standard(i['lyrics'])
            response.append(i)

    # 如果查询到歌词, 将第一个歌词写入到本地.
    if len(response) > 0 and path and os.path.isfile(path):
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            with open(lrc_path, "w") as file:
                file.write(response[0].get('lyrics'))

    _response = jsonify(response)
    _response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return jsonify(response)


@app.route('/lyrics/confirm', methods=['POST'])
def lyric_confirm():
    match require_auth(request=request, permission="wr"):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421

    data = request.json
    required_fields = ["path", "lyrics"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"缺少必要字段: {field}"}), 400

    path = data.get('path')
    lyrics = data.get('lyrics')

    if lyrics is None or lyrics.strip() == '':
        abort(400, "歌词内容为空")

    path = unquote_plus(path)

    if not os.path.isfile(path):
        abort(400, "不存在该音乐文件")

    lrc_path = os.path.splitext(path)[0] + '.lrc'

    with open(lrc_path, "w") as file:
        file.write(lyrics)
        logger.info(f"确认歌词成功: {path} ")

    return jsonify({"message": "歌词写入成功", "status": 0}), 200
