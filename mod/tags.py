from mutagen import File


def id3_lrc(path, lrc, read=False):
    from mutagen.id3 import ID3, USLT
    audio = ID3(path)
    if read:
        matching_keys = [key for key in audio.keys() if key.startswith("USLT")]
        for key in matching_keys:
            try:
                return audio[key].text
            except:
                continue
    else:
        # 设置歌词
        audio["USLT"] = USLT(encoding=3, lang="eng", text=lrc)
        # 保存更改
        audio.save(path)
        return True


def ogg_lrc(path, lrc, read=False):
    from mutagen.oggvorbis import OggVorbis
    # 读取 Ogg Vorbis 文件
    audio = OggVorbis(path)
    if read:
        return audio["lyrics"]
    else:
        # 设置歌词
        audio["lyrics"] = lrc
        # 保存更改
        audio.save()
        return True


def lrcs(path, lrc, read=False):
    tag_objs = [id3_lrc, ogg_lrc]
    for tag_obj in tag_objs:
        try:
            result = tag_obj(path, lrc, read)
            return result
        except Exception:
            continue
    return False


def w_file(path: str, tags: dict) -> int:
    audio = File(path, easy=True)
    title = tags.get("title", None)
    artist = tags.get("artist", None)
    album = tags.get("album", None)
    lyrics = tags.get("lyrics", None)
    if title is not None:
        audio["title"] = title
    if artist is not None:
        audio["artist"] = artist
    if album is not None:
        audio["album"] = album
    try:
        if lyrics is not None:
            audio["lyrics"] = lyrics
        audio.save()
        return 0
    except Exception as e:
        result = lrcs(path, lyrics)
        if not result:
            return -1
    try:
        audio.save()
    except Exception as e:
        return -2
    return 0


def r_lrc(path: str) -> str:
    audio = File(path, easy=True)
    lyrics = audio.get("lyrics", None)
    if lyrics is None:
        lyrics = lrcs(path, None, read=True)
    if type(lyrics) == list:
        return lyrics[0]
    return lyrics


if __name__ == "__main__":
    file_path = ""
