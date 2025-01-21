import requests

from mod import tools


class MiGuMusicClient:
    BASE_URL = "https://m.music.migu.cn/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
        'Referer': 'https://m.music.migu.cn/'
    }

    def fetch_lyric(self, song_id):
        url = f'https://music.migu.cn/v3/api/music/audioPlayer/getLyric?copyrightId={song_id}'
        res = requests.get(url, headers=self.header)
        return res.json()["lyric"]

    def fetch_id3_by_title(self, title):
        url = self.BASE_URL + f"migu/remoting/scr_search_tag?rows=10&type=2&keyword={title}&pgc=1"
        res = requests.get(url, headers=self.header)
        songs = res.json()["musics"]
        results = []
        for song in songs:
            lyrics = self.fetch_lyric(song['copyrightId'])
            results.append({
                "title": song['songName'],
                "album": song['albumName'],
                "artist": song['singerName'],
                "lrc": lyrics,
                "cover": song['cover'],
                "id": tools.calculate_md5(
                    f"title:{song['songName']};artists:{song['singerName']};album:{song['albumName']}", base='decstr')
            })
        return results


def search(title='', artist='', album='') -> list:
    migumusic = MiGuMusicClient()
    result = migumusic.fetch_id3_by_title(title)
    return result


if __name__ == "__main__":
    print(search(title="光辉岁月"))
