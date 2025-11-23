import json
import aiohttp
import asyncio
import logging

from functools import lru_cache

import urllib
from utils.data import hash_data
from utils import textcompare


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
ARTIST_SEARCH_URL = 'http://music.163.com/api/v1/artist/{}'
ALBUMS_SEARCH_URL = "http://music.163.com/api/artist/albums/{}?offset=0&total=true&limit=300"
ALBUM_INFO_URL = "http://music.163.com/api/album/{}?ext=true"


def listify(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


async def search_artist_blur(session: aiohttp.ClientSession, artist_blur, limit=1):
    """ 由于没有选择交互的过程, 因此 artist_blur 如果输入的不准确, 可能会查询到错误的歌手 """
    # logging.info('开始搜索: ' + artist_blur)

    num = 0
    if not artist_blur:
        logging.info('Missing artist. Skipping match')
        return None

    url = COMMON_SEARCH_URL_WANGYI.format(
        urllib.parse.quote(artist_blur.lower()), 100, 0, limit)
    artists = []
    try:
        json_data_r = await session.get(url, headers=headers)
        response = json.loads(await json_data_r.text())

        artist_results = response['result']
        num = int(artist_results['artistCount'])
        lim = min(limit, num)
        # logging.info('搜索到的歌手数量：' + str(lim))
        for i in range(lim):
            try:
                artists = listify(artist_results['artists'])
            except:
                logging.error('Error retrieving artist search results.')
    except:
        logging.error('Error retrieving artist search results.')
    if len(artists) > 0:
        return artists[0]
    return None


async def search_albums(session: aiohttp.ClientSession, artist_id):
    url = ALBUMS_SEARCH_URL.format(artist_id)
    json_data_r = await session.get(url, headers=headers)
    response = json.loads(await json_data_r.text())
    if response['code'] == 200:
        return response['hotAlbums']
    return None


def filter_and_get_album_id(album_list, album):
    most_similar = None
    highest_similarity = 0

    for candidate_album in album_list:
        if album == candidate_album['name']:
            return candidate_album['id']
        similarity = textcompare.association(album, candidate_album['name'])
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar = candidate_album
    return most_similar['id'] if most_similar is not None else None


async def get_album_info_by_id(session: aiohttp.ClientSession, album_id):
    url = ALBUM_INFO_URL.format(album_id)
    json_data_r = await session.get(url, headers=headers)
    response = json.loads(await json_data_r.text())
    if response['code'] == 200:
        return response['album']
    return None


async def get_album_info(session, artist, album):
    # 1. 根据 artist, 获取 artist_id
    if blur_result := await search_artist_blur(session, artist_blur=artist):
        artist_id = blur_result['id']
        # 2. 根据 artist_id 查询所有专辑
        if album_list := await search_albums(session, artist_id):
            # 3. 根据 album, 过滤, 并获取到 album_id
            if album_id := filter_and_get_album_id(album_list, album):
                # 4. 根据 album_id, 查询 album_info
                return await get_album_info_by_id(session, album_id)
    return None


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
    查询封面: 
        三者都传：获取歌曲封面
        不传歌曲标题：获取专辑封面 --- 传歌手/歌曲
        只传歌手名：获取歌手图片
    查询歌词:
        title 不能为空
        album, artist 这两个可以为空
    """
    if not any((title, artist, album)):
        return None

    async with aiohttp.ClientSession() as session:
        # 查询歌曲, 包括封面和歌词
        if title:
            return await search_track(session, title=title, artist=artist, album=album)
        elif artist and album:
            # 只查询专辑封面
            return await search_album(session, artist, album)
        elif artist:
            # 查询艺术家封面
            return await search_artist(session, artist)
        return None


async def search_artist(session, artist):
    # 1. 根据 artist, 获取 artist_id
    if blur_result := await search_artist_blur(session, artist_blur=artist):
        music_json_data: dict = {
            "cover": blur_result['img1v1Url']
        }
        return listify(music_json_data)
    return None


async def search_album(session, artist, album):
    if album_info := await get_album_info(session, artist, album):
        music_json_data: dict = {
            "cover": album_info['picUrl']
        }
        return listify(music_json_data)
    return None


async def search_track(session, title, artist, album):
    result_list = []
    limit = 10
    search_str = ' '.join([item for item in [title, artist, album] if item])
    url = COMMON_SEARCH_URL_WANGYI.format(search_str, 1, 0, 100)

    response = await session.get(url, headers=headers)

    if response.status != 200:
        return None

    song_info_t: str = await response.text()
    song_info: dict = json.loads(song_info_t)
    song_info: list[dict] = song_info["result"]["songs"]
    if len(song_info) < 1:
        return None
    candidate_songs = []
    for song_item in song_info:
        # 有些歌, 查询的 title 可能在别名里, 例如周杰伦的 八度空间-"分裂/离开", 有两个名字.
        song_names: list = song_item['alias']
        song_names.append(song_item['name'])
        artists = song_item.get("artists", None)
        singer_name = " ".join([x['name'] for x in artists]) if artists is not None else ""
        album_ = song_item.get("album", None)
        album_name = album_['name'] if album is not None else ''
        # 取所有名字中最高的相似度
        title_conform_ratio = max([textcompare.association(title, name) for name in song_names])

        artist_conform_ratio = textcompare.assoc_artists(artist, singer_name)
        album_conform_ratio = textcompare.association(album, album_name)

        ratio: float = (title_conform_ratio * (artist_conform_ratio + album_conform_ratio) / 2.0) ** 0.5

        if ratio >= 0.2:
            song_id = song_item['id']
            album_id = album_[
                'id'] if album is not None else None
            singer_id = [x['id'] for x in artists][0]
            candidate_songs.append(
                {'ratio': ratio, "item": {
                    "artist": singer_name,
                    "album": album_name,
                    "title": title,
                    "artist_id": singer_id,
                    "album_id": album_id,
                    "trace_id": song_id
                }})

    candidate_songs.sort(
        key=lambda x: x['ratio'], reverse=True)
    if len(candidate_songs) < 1:
        return None

    candidate_songs = candidate_songs[:min(len(candidate_songs), limit)]

    for candidate in candidate_songs:
        track = candidate['item']
        ratio = candidate['ratio']

        cover_url = await get_cover_url(session, track['album_id'])
        lyrics = await get_lyrics(session, track['trace_id'])

        # 结构化JSON数据
        music_json_data: dict = {
            "title": track['title'],
            "album": track['album'],
            "artist": track['artist'],
            "lyrics": lyrics,
            "cover": cover_url,
            "id": hash_data(
                title=track['title'], artist=track['artist'], album=track['album'], lyrics=lyrics)
        }

        result_list.append(music_json_data)
    return result_list


@lru_cache(maxsize=64)
def search(title='', artist='', album=''):
    return asyncio.run(a_search(title=title, artist=artist, album=album))


if __name__ == "__main__":
    print(search(album="十年"))