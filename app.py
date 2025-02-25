import logging
import sys
import os

from logging.handlers import RotatingFileHandler
from waitress import serve

# 导入其他模块前配置日志系统
logging.basicConfig(
    level=logging.INFO if not 'debug' in sys.argv else logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

os.makedirs(os.path.join(os.path.dirname(sys.argv[0]), 'logs'), exist_ok=True)
file_handler = RotatingFileHandler(
    os.path.join(os.path.dirname(sys.argv[0]), 'logs', 'log.txt'),
    maxBytes=1024*1024,
    backupCount=5
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('')
logger.addHandler(file_handler)


from mod import check_update
from mod.args import args
from api import *
from api import __import__


def run_server(debug=False):
    if not debug:
        # Waitress WSGI 服务器
        serve(app, host=args("server", "ip"), port=args("server", "port"), threads=32, channel_timeout=30)
    else:
        logger.debug("Debug模式已开启")
        logger.debug(f"Version: {args.version}")
        logger.debug(f"Auth: {args('auth')}")
        app.run(host='0.0.0.0', port=args("server", "port"), debug=True)


if __name__ == '__main__':
    # 对Python版本进行检查（要求Python 3.10+）
    if sys.version_info < (3, 10):
        raise RuntimeError(
            "Python 3.10+ required, but you are using Python {}.{}.{}.".format(*sys.version_info[:3])
        )
    
    # 日志级别根据debug参数调整
    if args.debug:
        logging.getLogger('').setLevel(logging.DEBUG)

    logger.info("正在启动服务器")
    logger.info("您可通过爱发电支持我们，爱发电主页 https://afdian.com/a/ghacg")
    check_update.run(version=args.version)
    # 注册 Blueprint 到 Flask 应用
    app.register_blueprint(v1_bp)
    # 启动
    run_server(args.debug)
    exit()
    