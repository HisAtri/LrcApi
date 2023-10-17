import time
import base64
import requests
import concurrent.futures


def get_lyrics_from_net(title, artist, album):
    if title is None and artist is None:
        return None
    title = "" if title is None else title
    artist = "" if artist is None else artist
    searcher = title + artist

    # 使用歌曲名和作者名查询歌曲
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 LrcAPI/1.1', }
    # 第一层Json，要求获得Hash值
    response = requests.get(
        f'http://mobilecdn.kugou.com/api/v3/search/song?format=json&keyword={searcher}&page=1&pagesize=2&showtype=1',
        headers=headers)
    if response.status_code == 200:
        song_info = response.json()
        try:
            songhash = song_info["data"]["info"][0]["hash"]
            # 第二层Json，要求获取歌词ID和AccessKey
            response2 = requests.get(
                f"https://krcs.kugou.com/search?ver=1&man=yes&client=mobi&keyword=&duration=&hash={songhash}&album_audio_id=",
                headers=headers)
            lyrics_info = response2.json()
            lyrics_id = lyrics_info["candidates"][0]["id"]
            lyrics_key = lyrics_info["candidates"][0]["accesskey"]
            # 第三层Json，要求获得并解码Base64
            response3 = requests.get(
                f"http://lyrics.kugou.com/download?ver=1&client=pc&id={lyrics_id}&accesskey={lyrics_key}&fmt=lrc&charset=utf8",
                headers=headers)
            lyrics_data = response3.json()
            lyrics_encode = lyrics_data["content"]
            lrc_text = base64.b64decode(lyrics_encode).decode('utf-8')
            return lrc_text

        except:
            time.sleep(10)
            return None


def api_2(title, artist, album):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 LrcAPI/1.1',
    }
    url = f"https://lrc.xms.mx/lyrics?title={title}&artist={artist}&album={album}&path=None&limit=1"
    try:
        res = requests.get(url, headers=headers)
        return res.text
    except:
        time.sleep(10)
        return None


def main(title, artist, album):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交各API函数到线程池中执行
        future_a = executor.submit(get_lyrics_from_net, title, artist, album)
        future_b = executor.submit(api_2, title, artist, album)
        # 等待任意一个API完成
        done, not_done = concurrent.futures.wait([future_a, future_b], return_when=concurrent.futures.FIRST_COMPLETED)
        # 获取已完成线程的返回结果
        lyrics_text = done.pop().result()
    return lyrics_text


if __name__ == "__main__":
    print(main("钟无艳", "谢安琪", "N"))
