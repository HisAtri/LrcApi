from . import *

import requests

from flask import request, abort, redirect
from urllib.parse import unquote_plus
from mygo.devtools import no_error
from mod.auth import require_auth_decorator

from mod import searchx

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"}

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
    abort(404)          # 达到最大重定向次数仍未获得 200 状态码，放弃


def local_cover_search(title: str, artist: str, album: str):
    result: list = searchx.search_all(title=title, artist=artist, album=album, timeout=30)
    for item in result:
        if cover_url := item.get('cover'):
            res = requests.get(cover_url, headers=headers)
            if res.status_code == 200:
                return res.content, 200, {"Content-Type": res.headers['Content-Type']}

@app.route('/cover', methods=['GET'], endpoint='cover_endpoint')
@require_auth_decorator(permission='rw')
@cache.cached(timeout=86400, key_prefix=make_cache_key)
@no_error(exceptions=AttributeError)
def cover_api():
    title = unquote_plus(request.args.get('title', ''))
    artist = unquote_plus(request.args.get('artist', ''))
    album = unquote_plus(request.args.get('album', ''))
    req_args = {key: request.args.get(key) for key in request.args}
    # 构建目标URL
    target_url = 'http://api.lrc.cx/cover?' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    result = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"})
    if result.status_code == 200:
        return result.content, 200, {"Content-Type": result.headers['Content-Type']}
    elif res := local_cover_search(title, artist, album):
        return res
    elif result.status_code == 404:
        abort(404)
    else:
        abort(500, '服务存在错误，暂时无法查询')


@v1_bp.route('/cover/<path:s_type>', methods=['GET'], endpoint='cover_new_endpoint')
@require_auth_decorator(permission='r')
@cache.cached(timeout=86400, key_prefix=make_cache_key)
@no_error(exceptions=AttributeError)
def cover_new(s_type):
    __endpoints__ = ["music", "album", "artist"]
    if s_type not in __endpoints__:
        abort(404)
    req_args = {key: request.args.get(key) for key in request.args}
    target_url = f'http://api.lrc.cx/cover/{s_type}/' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    return redirect(target_url, 302)
