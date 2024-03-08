import datetime

from . import *


@app.route('/time', methods=['GET'])
@v1_bp.route('/time', methods=['GET'])
@cache.cached(timeout=50, key_prefix=make_cache_key)
def get_time():
    """
    获取时间
    :return:
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
