from . import *

import requests

from flask import request, abort, redirect


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


@app.route('/cover', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_api():
    req_args = {key: request.args.get(key) for key in request.args}
    # 构建目标URL
    target_url = 'http://api.lrc.cx/cover?' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    result = requests.get(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"})
    if result.status_code == 200:
        return result.content, 200, {"Content-Type": result.headers['Content-Type']}
    elif result.status_code == 404:
        abort(404)
    else:
        abort(500)


@v1_bp.route('/cover/<path:s_type>', methods=['GET'])
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def cover_new(s_type):
    __endpoints__ = ["music", "album", "artist"]
    if s_type not in __endpoints__:
        abort(404)
    req_args = {key: request.args.get(key) for key in request.args}
    target_url = f'http://api.lrc.cx/cover/{s_type}/' + '&'.join([f"{key}={req_args[key]}" for key in req_args])
    return redirect(target_url, 302)
