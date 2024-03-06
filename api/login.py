from . import *

import logging

from flask import request, redirect, jsonify, render_template_string, make_response

from mod.auth import webui, cookie
from mod.auth.authentication import require_auth
from mod.args import GlobalArgs

args = GlobalArgs()
logger = logging.getLogger(__name__)


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
