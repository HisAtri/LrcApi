import base64
import requests
import asyncio
from fake_useragent import UserAgent
from mod import textcompare


ua = UserAgent().chrome


async def kugou(title, artist, album):
    headers = {'User-Agent': ua, }
    limit = 10
    # 第一层Json，要求获得Hash值
    response = requests.get(
        f'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={title} {artist} {album}&page=1&pagesize=2&showtype=1',
        headers=headers,
        timeout=10)
    if response.status_code == 200:
        song_info = response.json()["data"]["info"]
        if len(song_info) >= 1:
            ratio_max = 0.2
            for index in range(min(limit, len(song_info))):
                song_item = song_info[index]
                song_name = song_item["songname"]
                singer_name = song_item.get("singername", "")
                song_hash = song_item["hash"]
                album_name = song_item.get("album_name", "")
                title_conform_ratio = textcompare.association(title, song_name)
                artist_conform_ratio = textcompare.assoc_artists(artist, singer_name)
                # 计算两个指标的几何平均值；区间范围(0,1]
                ratio = (title_conform_ratio * artist_conform_ratio) ** 0.5
                ratio_max = max(ratio, ratio_max)
                if ratio >= ratio_max:
                    response2 = requests.get(
                        f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={song_hash}&album_audio_id=",
                        headers=headers,
                        timeout=10)
                    lyrics_info = response2.json()
                    lyrics_id = lyrics_info["candidates"][0]["id"]
                    lyrics_key = lyrics_info["candidates"][0]["accesskey"]
                    # 第三层Json，要求获得并解码Base64
                    response3 = requests.get(
                        f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyrics_id}&accesskey={lyrics_key}&fmt=lrc&charset=utf8",
                        headers=headers,
                        timeout=10)
                    lyrics_data = response3.json()
                    lyrics_encode = lyrics_data["content"]  # 这里是Base64编码的数据
                    lrc_text = base64.b64decode(lyrics_encode).decode('utf-8')  # 这里解码
                    return lrc_text
    await asyncio.sleep(10)
    return None


async def api_2(title, artist, album):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 LrcAPI/1.1',
    }
    url = f"https://lrc.xms.mx/lyrics?title={title}&artist={artist}&album={album}&path=None&limit=1&api=lrcapi"
    try:
        res = requests.get(url, headers=headers, timeout=30)
        if res.status_code < 300:
            return res.text
        else:
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code < 300:
                return res.text
    except:
        await asyncio.sleep(10)
        return None
    return None


api_list = [kugou, api_2]


# 高IO任务由于存在GIL，应当用异步算法
async def aw_main(title, artist, album):
    await_list = [func(title, artist, album) for func in api_list]

    # 使用 asyncio.as_completed 获取完成的任务
    for coro in asyncio.as_completed(await_list):
        result = await coro
        return result


async def aw_all(title, artist, album):
    await_list = [func(title, artist, album) for func in api_list]
    all_list = []
    # 使用 asyncio.as_completed 获取完成的任务
    for coro in asyncio.as_completed(await_list):
        result = await coro
        all_list.append(result)
    return all_list


def main(title, artist, album):
    return asyncio.run(aw_main(title, artist, album))


def allin(title, artist, album):
    return asyncio.run(aw_all(title, artist, album))


if __name__ == "__main__":
    print(allin("醉花阴", "洛天依", ""))
