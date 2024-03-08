import requests
import logging
import threading

logger = logging.getLogger(__name__)


def get_version():
    api = "https://data.jsdelivr.com/v1/package/gh/hisatri/lrcapi"
    data = requests.get(api).json()
    version = data['versions'][0]
    return version


def version_upper(latest: str, app_version: str) -> bool:
    """
    检查是否有新版本
    :param latest: 最新版本号
    :param app_version: 当前版本号
    """
    v1 = tuple(map(int, latest.split('.')))
    v2 = tuple(map(int, app_version.split('.')))
    for i in range(3):
        if v1[i] > v2[i]:
            return True
        elif v1[i] < v2[i]:
            return False


def check_update(version):
    logger.info("正在检查更新")
    try:
        latest_version = get_version()
        if version_upper(latest_version, version):
            logger.info(f"发现新版本:Release v{latest_version}")
            return latest_version
        else:
            logger.info("当前已是最新版本")
            return False
    except:
        logger.warning("暂时无法获取最新版本号")
        return False


def run(version):
    # 启动线程后直接返回
    t = threading.Thread(target=check_update, args=(version,))
    t.start()


if __name__ == '__main__':
    run("0.0.1")
    input(":")
