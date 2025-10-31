import re


def standard_line(lrc_text: str):
    # 定义匹配时间标签的正则表达式
    pattern = re.compile(r'\[(\d+[.:]\d+[.:]\d+)]')
    # 使用正则表达式查找所有匹配的时间标签
    matches = pattern.findall(lrc_text)
    # 遍历匹配的时间标签，替换毫秒位
    for match in matches:
        old_time_label = match
        minutes, seconds, millisecond = map(str, re.split('[:.]', old_time_label))
        minute_str = ('00'+minutes)[-2:] if int(minutes) < 100 else str(minutes)
        second_str = ('00'+seconds)[-2:]
        millisecond_str = (millisecond+'000')[:3]
        new_time_label = f"{minute_str}:{second_str}.{millisecond_str}"
        lrc_text = lrc_text.replace(old_time_label, new_time_label)

    return lrc_text


def standard(lrc_text: str) -> str:
    if not isinstance(lrc_text, str):
        return ''
    # 替换零宽字符和换行符
    lrc_text = (
        lrc_text.replace("\r\n", "\n")
        .replace("\ufeff", "")
        .replace("\u200b", "")
    )
    parse_string = ''
    # 使用[分割字符串，得到每一行歌词
    lines = lrc_text.split('[')
    for line_index in range(len(lines)):
        if line_index > 0:
            line = '[' + lines[line_index]
        else:
            line = lines[line_index]
        parse_string += standard_line(line)

    return parse_string


def is_valid(lrc_text: str) -> bool:
    if type(lrc_text) is not str:
        return False
    pattern = re.compile(r'\[(\d+:\d+\.\d{3})]')
    matches = pattern.findall(lrc_text)
    if matches:
        return True
    else:
        return False


if __name__ == "__main__":
    lrc = """
    [00:02.05]愿得一人心
    [00:08.64]词：胡小健 曲：罗俊霖
    [00:11.14]演唱： 李行亮，雨宗林
    [00:24.93]
    [00:27.48]曾在我背包小小夹层里的那个人
    [00:32.31]陪伴我漂洋过海经过每一段旅程
    [00:37.38]隐形的稻草人 守护我的天真
    [00:42.43]曾以为爱情能让未来只为一个人
    [00:47.50]关了灯依旧在书桌角落的那个人
    [00:52.68]变成我许多年来纪念爱情的标本
    [00:57.57]消失的那个人 回不去的青春
    [01:02.69]忘不了爱过的人才会对过往认真
    [01:09.71]只愿得一人心 白首不分离
    [01:14.71]这简单的话语 需要巨大的勇气
    [01:19.73]没想过失去你 却是在骗自己
    [01:25.34]最后你深深藏在我的歌声里
    [00:02.05]愿得一人心
    [00:08.64]词：胡小健 曲：罗俊霖
    [00:11.14]演唱： 李行亮，雨宗林
    [00:24.93]
    [00:27.48]曾在我背包小小夹层里的那个人
    [00:32.31]陪伴我漂洋过海经过每一段旅程
    [00:37.38]隐形的稻草人 守护我的天真
    [00:42.43]曾以为爱情能让未来只为一个人
    [00:47.50]关了灯依旧在书桌角落的那个人
    [00:52.68]变成我许多年来纪念爱情的标本
    [00:57.57]消失的那个人 回不去的青春
    [01:02.69]忘不了爱过的人才会对过往认真
    [01:09.71]只愿得一人心 白首不分离
    [01:14.71]这简单的话语 需要巨大的勇气
    [01:19.73]没想过失去你 却是在骗自己
    [01:25.34]最后你深深藏在我的歌声里
    [00:02.05]愿得一人心
    [00:08.64]词：胡小健 曲：罗俊霖
    [00:11.14]演唱： 李行亮，雨宗林
    [00:24.93]
    [00:27.48]曾在我背包小小夹层里的那个人
    [00:32.31]陪伴我漂洋过海经过每一段旅程
    [00:37.38]隐形的稻草人 守护我的天真
    [00:42.43]曾以为爱情能让未来只为一个人
    [00:47.50]关了灯依旧在书桌角落的那个人
    [00:52.68]变成我许多年来纪念爱情的标本
    [00:57.57]消失的那个人 回不去的青春
    [01:02.69]忘不了爱过的人才会对过往认真
    [01:09.71]只愿得一人心 白首不分离
    [01:14.71]这简单的话语 需要巨大的勇气
    [01:19.73]没想过失去你 却是在骗自己
    [01:25.34]最后你深深藏在我的歌声里"""
    print(standard(lrc))

    from devtools import Benchmark
    b = Benchmark(threads=1, rounds=10000)
    print(b.run(standard, lrc))
