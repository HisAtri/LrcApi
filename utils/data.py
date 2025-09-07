from hashlib import md5
import json


def hash_data(title: str, artist: str, album: str, lyrics: str) -> str:
    data = {
        "title": title,
        "artist": artist,
        "album": album,
        "lyrics": lyrics
    }
    return md5(json.dumps(data).encode()).hexdigest()
