import json
import aiohttp
import asyncio
import base64
import random
import string
import time
import logging

from functools import lru_cache

from mod import textcompare
from mod import tools

from mygo.devtools import no_error

headers: dict = {'User-Agent': '{"percent": 21.4, "useragent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36", "system": "Chrome '
                         '116.0 Win10", "browser": "chrome", "version": 116.0, "os": "win10"}', }
logger = logging.getLogger(__name__)


async def get_cover(session: aiohttp.ClientSession, m_hash: str, m_id: int|str) -> str:
    def _dfid(num):
        random_str = ''.join(random.sample((string.ascii_letters + string.digits), num))
        return random_str

    # 获取a-z  0-9组成的随机23位数列
    def _mid(num):
        random_str = ''.join(random.sample((string.ascii_letters[:26] + string.digits), num))
        return random_str

    music_url = 'https://wwwapi.kugou.com/yy/index.php'
    parameter = {
        'r': 'play/getdata',
        'hash': m_hash,
        'dfid': _dfid(23),
        'mid': _mid(23),
        'album_id': m_id,
        '_': str(round(time.time() * 1000))  # 时间戳
    }
    json_data_r = await session.get(music_url, headers=headers, params=parameter)
    json_data = json.loads(await json_data_r.text())
    if json_data.get("data"):
        return json_data['data'].get("img")
    return ""


async def a_search(title='', artist='', album=''):
    if not any((title, artist, album)):
        return None
    result_list = []
    limit = 3
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f"http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={' '.join([item for item in [title, artist, album] if item])}&page=1&pagesize=2&showtype=1",
                headers=headers) as response:
            if response.status == 200:
                song_info_t: str = await response.text()
                song_info: dict = json.loads(song_info_t)
                song_info: list[dict] = song_info["data"]["info"]
                if len(song_info) >= 1:
                    for song_item in song_info:
                        song_name = song_item["songname"]
                        singer_name = song_item.get("singername", "")
                        song_hash = song_item["hash"]
                        album_id = song_item["album_id"]
                        album_name = song_item.get("album_name", "")
                        title_conform_ratio = textcompare.association(title, song_name)
                        artist_conform_ratio = textcompare.assoc_artists(artist, singer_name)
                        ratio: float = (title_conform_ratio * (artist_conform_ratio+1)/2) ** 0.5
                        if ratio >= 0.2:
                            async with session.get(
                                    f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={song_hash}&album_audio_id=",
                                    headers=headers) as response2:
                                lyrics_info = await response2.json()
                                if not lyrics_info["candidates"]:
                                    continue
                                lyrics_id = lyrics_info["candidates"][0]["id"]
                                lyrics_key = lyrics_info["candidates"][0]["accesskey"]
                            # 第三层Json，要求获得并解码Base64
                            async with session.get(
                                    f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyrics_id}&accesskey={lyrics_key}&fmt=lrc&charset=utf8",
                                    headers=headers) as response3:
                                lyrics_data = await response3.json()
                                lyrics_encode = lyrics_data["content"]  # 这里是Base64编码的数据
                                lrc_text = tools.standard_lrc(base64.b64decode(lyrics_encode).decode('utf-8'))  # 这里解码
                                # 结构化JSON数据
                                music_json_data: dict = {
                                    "title": song_name,
                                    "album": album_name,
                                    "artists": singer_name,
                                    "lyrics": lrc_text,
                                    "cover": await get_cover(session, song_hash, album_id),
                                    "hash": tools.calculate_md5(
                                        f"title:{song_name};artists:{singer_name};album:{album_name}")
                                }
                                result_list.append({
                                    "data": music_json_data,
                                    "ratio": ratio
                                })
                                if len(result_list) > limit:
                                    break
            else:
                return None
        sort_li: list[dict] = sorted(result_list, key=lambda x: x['ratio'], reverse=True)
        return [i.get('data') for i in sort_li]


@lru_cache(maxsize=64)
@no_error(throw=logger.info,
          exceptions=(aiohttp.ClientError, asyncio.TimeoutError, KeyError, IndexError, AttributeError))
def search(title='', artist='', album=''):
    return asyncio.run(a_search(title=title, artist=artist, album=album))


if __name__ == "__main__":
    print(search(album="十年"))
