import shutil

from flask import Flask, Blueprint, request
from flask_caching import Cache


app = Flask(__name__)

v1_bp = Blueprint('v1', __name__, url_prefix='/api/v1')
# Blueprint直接复制app配置项
v1_bp.config = app.config.copy()
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
def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return path + args


__all__ = ['app', 'v1_bp', 'cache', 'make_cache_key']
