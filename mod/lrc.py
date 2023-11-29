import re


def standard(lrc_text: str):
    # 定义匹配时间标签的正则表达式
    pattern = re.compile(r'\[(\d+:\d+\.\d{2})\]')

    # 使用正则表达式查找所有匹配的时间标签
    matches = pattern.findall(lrc_text)

    # 遍历匹配的时间标签，替换毫秒位
    for match in matches:
        old_time_label = match
        minutes, seconds, millisecond = map(int, re.split(':|\.', old_time_label))
        new_time_label = f"{minutes:02d}:{seconds:02d}.{millisecond:02d}0"
        lrc_text = lrc_text.replace(old_time_label, new_time_label)

    return lrc_text


def is_valid(lrc_text: str):
    pattern = re.compile(r'\[(\d+:\d+\.\d{2})\]')
    matches = pattern.findall(lrc_text)
    if matches:
        return True
    else:
        return False


if __name__ == "__main__":
    lrc = "[00:00.00]歌词1\n[03:23.22]歌词2\n[05:45.55]歌词3"
    result = standard(lrc)
    print(result)
