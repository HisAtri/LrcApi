import requests
import logging
from mod.args import args


logger = logging.getLogger(__name__)


headers = {
    "Host": "127.0.0.1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 LrcAPI",
    "Authorization": args("token")
}


def search(title='', artist='', album='') -> list:
    try:
        url = f"https://api.lrc.cx/jsonapi?title={title}&artist={artist}&album={album}&path=None&limit=1&api=lrcapi"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            logger.warning("锂API接口的Token无效，请检查配置")
            return []
        else:
            logger.warning(f"锂API接口请求失败，状态码：{response.status_code}")
            return []
    except Exception as e:
        logger.error(f"锂API接口请求失败，错误：{e}")
        return []


if __name__ == "__main__":
    print(search(title="光辉岁月"))
