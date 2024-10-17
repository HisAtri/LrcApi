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


def read_file_with_encoding(file_path: str, encodings: list[str]):
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
            file_content: str | None = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
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
        title = unquote_plus(request.args.get('title', ''))
        artist = unquote_plus(request.args.get('artist', ''))
        album = unquote_plus(request.args.get('album', ''))
        result: list = searchx.search_all(title=title, artist=artist, album=album, timeout=30)
        if not result[0].get('lyrics'):
            return "Lyrics not found.", 404
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
    if path:
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
            if lyric := i.get('lyrics'):
                i['lyrics'] = lrc.standard(lyric)
                response.append(i)
    _response = jsonify(response)
    _response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return jsonify(response)
