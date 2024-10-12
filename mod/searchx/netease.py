import json
import aiohttp
import asyncio
import logging

from functools import lru_cache
from Levenshtein import distance
from mod import tools
from mygo.devtools import no_error

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0',
    'origin': 'https://music.163.com',
    'referer': 'https://music.163.com',
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# type: 1-songs, 10-albums, 100-artists, 1000-playlists
COMMON_SEARCH_URL_WANGYI = 'https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s={}&type={}&offset={}&total=true&limit={}'
ALBUM_SEARCH_URL_WANGYI = 'https://music.163.com/api/album/{}?ext=true'
LYRIC_URL_WANGYI = 'https://music.163.com/api/song/lyric?id={}&lv=1&tv=1'


def levenshtein_similarity(a, b):
    return 1 - (distance(a, b) / max(len(a), len(b)))


async def get_cover_url(session: aiohttp.ClientSession, album_id: int):
    url = ALBUM_SEARCH_URL_WANGYI.format(album_id)
    json_data_r = await session.get(url, headers=headers)
    json_data = json.loads(await json_data_r.text())
    if json_data.get('album', False) and json_data.get('album').get('picUrl', False):
        return json_data['album']['picUrl']
    return None


async def get_lyrics(session: aiohttp.ClientSession, track_id: int):
    url = LYRIC_URL_WANGYI.format(track_id)
    json_data_r = await session.get(url, headers=headers)
    json_data = json.loads(await json_data_r.text())
    if json_data.get('lrc', False) and json_data.get('lrc').get('lyric', False):
        return json_data['lrc']['lyric']
    return None


async def a_search(title='', artist='', album=''):
    """
    网易上有太多的自制音乐, 搜起来一大堆乱七八糟的. 
    就是说, 只有歌名的情况下, 搜出来的结果十有八九是错的. 
    而有 artist + album + title 组合搜索, 准确性可以提高很多很多
    """
    if not any((title, artist, album)):
        return None
    result_list = []
    limit = 3
    async with aiohttp.ClientSession() as session:
        search_str = ' '.join(
            [item for item in [title, artist, album] if item])
        async with session.get(COMMON_SEARCH_URL_WANGYI.format(search_str, 1, 0, 100),  headers=headers) as response:
            if response.status == 200:
                song_info_t: str = await response.text()
                song_info: dict = json.loads(song_info_t)
                song_info: list[dict] = song_info["result"]["songs"]
                if len(song_info) < 1:
                    return None
                candidate_songs = []
                for song_item in song_info:
                    song_name = song_item["name"]
                    artists = song_item.get("artists", None)
                    singer_name = " ".join(
                        [x['name'] for x in artists]) if artists is not None else ""
                    album_ = song_item.get("album", None)
                    album_name = album_[
                        'name'] if album is not None else ''

                    title_conform_ratio = levenshtein_similarity(
                        title, song_name) if len(title) * len(song_name) > 0 else 0.0
                    artist_conform_ratio = levenshtein_similarity(
                        artist, singer_name) if len(artist) * len(singer_name) > 0 else 0.0
                    album_conform_ratio = levenshtein_similarity(
                        album, album_name) if len(album) * len(album_name) > 0 else 0.0

                    ratio: float = (title_conform_ratio +
                                    album_conform_ratio +
                                    artist_conform_ratio) / 3.0

                    if ratio >= 0.5:
                        song_id = song_item['id']
                        album_id = album_[
                            'id'] if album is not None else None
                        singer_id = [x['id'] for x in artists][0]
                        candidate_songs.append(
                            {'ratio': ratio, "item": {
                                "artist": singer_name,
                                "album": album_name,
                                "title": song_name,
                                "artist_id": singer_id,
                                "album_id": album_id,
                                "trace_id": song_id
                            }})

                candidate_songs.sort(
                    key=lambda x: x['ratio'], reverse=True)
                if len(candidate_songs) < 1:
                    return None

                candidate_songs = candidate_songs[:min(
                    len(candidate_songs), limit)]

                for candidate in candidate_songs:
                    track = candidate['item']
                    ratio = candidate['ratio']

                    cover_url = await get_cover_url(session, track['album_id'])
                    lyrics = await get_lyrics(session, track['trace_id'])

                    # 结构化JSON数据
                    music_json_data: dict = {
                        "title": track['title'],
                        "album": track['album'],
                        "artists": track['artist'],
                        "lyrics": lyrics,
                        "cover": cover_url,
                        "hash": tools.calculate_md5(
                            f"title:{track['title']};artists:{track['artist']};album:{track['album']}")
                    }

                    result_list.append(music_json_data)
            else:
                return None
        return result_list


@lru_cache(maxsize=64)
@no_error(throw=logger.info,
          exceptions=(aiohttp.ClientError, asyncio.TimeoutError, KeyError, IndexError, AttributeError))
def search(title='', artist='', album=''):
    return asyncio.run(a_search(title=title, artist=artist, album=album))


if __name__ == "__main__":
    print(search(album="十年"))
