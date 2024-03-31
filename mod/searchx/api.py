import requests


headers = {
    "Host": "127.0.0.1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
}


def search(title='', artist='', album='') -> list:
    try:
        url = f"http://cn.lrc.cx:28884/jsonapi?title={title}&artist={artist}&album={album}&path=None&limit=1&api=lrcapi"
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return []


if __name__ == "__main__":
    print(search(title="光辉岁月"))
