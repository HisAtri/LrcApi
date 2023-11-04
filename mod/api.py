import time
import base64
import requests
import concurrent.futures


def kugou(title, artist, album):
    if title is None and artist is None:
        return None
    title = "" if title is None else title
    artist = "" if artist is None else artist
    searcher = title + artist

    # 使用歌曲名和作者名查询歌曲
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 LrcAPI/1.1',
    }
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
    url = f"https://lrc.xms.mx/lyrics?title={title}&artist={artist}&album={album}&path=None&limit=1&api=lrcapi"
    try:
        res = requests.get(url, headers=headers)
        return res.text
    except:
        time.sleep(10)
        return None


def migu(title, artist, album):
    headers = {
        "Referer": "http://music.migu.cn/"
    }
    search_str = title + artist + album
    search_response = requests.get(
        f"https://pd.musicapp.migu.cn/MIGUM2.0/v1.0/content/search_all.do?&ua=Android_migu&version=5.0.1&text={search_str}&pageNo=1&pageSize=10&searchSwitch={{\"song\":1,\"album\":0,\"singer\":0,\"tagSong\":0,\"mvSong\":0,\"songlist\":0,\"bestShow\":1}}")
    res_json = search_response.json()
    result = res_json["songResultData"]["result"]
    for music_detail in result:
        if (music_detail["resourceType"] == "2") & (music_detail["name"] == title):
            lyrics_url = music_detail["lyricUrl"]
            lyrics_response = requests.get(lyrics_url, headers=headers)
            return lyrics_response.text
    time.sleep(10)
    return None


api_list = [kugou, api_2, migu]


def main(title, artist, album):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # 提交各API函数到线程池中执行
        task_list = []
        for task in api_list:
            task_list.append(executor.submit(task, title, artist, album))
        # 等待任意一个API完成
        done, not_done = concurrent.futures.wait(task_list, return_when=concurrent.futures.FIRST_COMPLETED)
        # 获取已完成线程的返回结果
        lyrics_text = done.pop().result()
    return lyrics_text


def allin(title, artist, album):
    lrc_list = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        def request_lrc(task):
            lrc = task(title, artist, album)
            if lrc:
                lrc_list.append(lrc)

        for task in api_list:
            future = executor.submit(request_lrc, task)
            futures.append(future)

        # 等待所有线程完成或超时
        try:
            concurrent.futures.wait(futures, timeout=30)
        except concurrent.futures.TimeoutError:
            pass

        # 取消未完成的任务
        for future in futures:
            future.cancel()

    return lrc_list


if __name__ == "__main__":
    print(allin("钟无艳", "谢安琪", "N"))
