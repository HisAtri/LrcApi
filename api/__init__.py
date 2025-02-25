import shutil
import logging
import sys
import os

from flask import Flask, Blueprint, request, g
from flask_caching import Cache
import time

app = Flask(__name__)
logger = logging.getLogger(__name__)

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')
v1_bp.config = app.config.copy()

navidrome_bp = Blueprint('navidrome', __name__, url_prefix='/api/navidrome')
navidrome_bp.config = app.config.copy()


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
def make_cache_key(*args, **kwargs) -> str:
    path:str = request.path
    args:str = str(hash(frozenset(request.args.items())))
    auth_key:str = str(request.headers.get('Authorization', '')
                       or request.headers.get('Authentication', ''))
    cookie:str = str(request.cookies.get('api_auth_token', ''))
    return path + args + auth_key + cookie


@app.before_request
def before_request():
    """
    请求前处理
    记录请求开始时间，用于计算请求处理时长
    """
    g.start_time = time.time()
    logger.info(f"收到请求: {request.method} {request.path}")


@app.after_request
def after_request(response):
    """
    请求后处理
    1. 添加通用响应头
    2. 记录请求处理时长
    3. 记录响应状态
    """
    # 添加通用响应头
    response.headers['Server'] = 'LrcApi'
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    
    # 计算并记录请求处理时长
    if hasattr(g, 'start_time'):
        duration = time.time() - g.start_time
        logger.info(f"请求处理完成: {request.method} {request.path} - 状态码: {response.status_code} - 耗时: {duration:.3f}s")
    
    return response


def get_base_path():
    """
    获取主程序所在目录（基于入口脚本路径）
    """
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
        
    # 判断是否以模块方式运行
    if __package__:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))


src_path = os.path.join(get_base_path(), 'src')  # 静态资源路径

__all__ = ['app', 'v1_bp', 'cache', 'make_cache_key', 'logger', 'src_path']
