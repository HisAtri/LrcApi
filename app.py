import logging
import sys

from waitress import serve

from mod import check_update
from mod.args import args
from mod.dev.debugger import debugger
from api import *
from api import __import__


def run_server(debug=False):
    if not debug:
        # Waitress WSGI 服务器
        serve(app, host=args("server", "ip"), port=args("server", "port"), threads=32, channel_timeout=30)
    else:
        debugger.debug = True
        debugger.log("info", "Debug模式已开启")
        debugger.log("info", f"Version: {args.version}")
        debugger.log("info", f"Auth: {args('auth')}")
        app.run(host='0.0.0.0', port=args("server", "port"), debug=True)


if __name__ == '__main__':
    # 对Python版本进行检查（要求Python 3.10+）
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Python 3.10+ required, but you are using Python {}.{}.{}.".format(*sys.version_info[:3])
        )
    # 日志配置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('')
    logger.info("正在启动服务器")
    logger.info("您可通过爱发电支持我们，爱发电主页 https://afdian.com/a/ghacg")
    check_update.run(version=args.version)
    # 注册 Blueprint 到 Flask 应用
    app.register_blueprint(v1_bp)
    # 启动
    run_server(args.debug)

