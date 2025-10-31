import hashlib
import re


def calculate_md5(string: str, base="hexstr"):
    """
    计算字符串的 MD5 哈希值

    参数：
    - string: 要计算哈希值的字符串
    - base: 返回结果的表示形式，可选值为 "hex"（十六进制，默认）、"dec"（十进制）、"bin"（二进制）
    返回：
    - 根据指定 base 返回相应表示形式的 MD5 哈希值
    """
    md5_hash = hashlib.md5()
    # 将字符串转换为字节流并进行 MD5 计算
    md5_hash.update(string.encode('utf-8'))
    # 根据 base 参数返回相应的结果
    if base == "hex":
        # 十六进制->str
        md5_hex = md5_hash.hexdigest()
        return md5_hex
    elif base == "dec":
        # 十进制表示->int
        md5_dec = int(md5_hash.hexdigest(), 16)  # 将十六进制转换为十进制
        return md5_dec
    elif base == "decstr":
        # 十进制表示->int
        md5_dec = int(md5_hash.hexdigest(), 16)  # 将十六进制转换为十进制
        return str(md5_dec)
    elif base == "bin":
        # 二进制表示->bin
        md5_bin = format(int(md5_hash.hexdigest(), 16), '0128b')  # 将十六进制转换为二进制，补齐到128位
        return md5_bin
    elif base == "hexstr":
        md5_bytes = md5_hash.digest()
        return md5_bytes.hex()
    else:
        raise ValueError("Invalid base. Supported values are 'hex', 'dec', 'hexstr', and 'bin'.")


def merge_dictionaries(dict_a: dict, dict_b: dict) -> dict:
    """
    合并两字典中的有效数据，前者优先
    :param dict_a:
    :param dict_b:
    :return:
    """
    merged_dict = {}
    if type(dict_a) is not dict:
        return dict_b
    # 遍历A和B的所有键
    for key in set(dict_a.keys()) | set(dict_b.keys()):
        # 判断A和B中对应键的值
        value_a = dict_a.get(key)
        value_b = dict_b.get(key)
        # 如果A和B中都有有效数据，则优先取A的值
        if value_a and value_b:
            merged_dict[key] = value_a
        # 如果A的值无效，则取B的值
        elif not value_a:
            merged_dict[key] = value_b
        # 如果B的值无效，则取A的值
        elif not value_b:
            merged_dict[key] = value_a
        else:
            merged_dict[key] = value_a
    return merged_dict


def standard_lrc(lrc_text: str) -> str:
    if not lrc_text or type(lrc_text) is not str:
        return lrc_text
    elif '[' in lrc_text and ']' in lrc_text:
        # 去除零宽字符
        lrc_text = re.sub(r'[\ufeff\u200b]', '',
                          lrc_text.replace("\r\n", "\n"))
        pattern = re.compile(r'\[([^]]+)]')
        # 使用findall方法找到所有匹配的字符串
        matches = pattern.findall(lrc_text)
        for match_s in matches:
            replacement = '[' + ']['.join(match_s.split(',')) + ']'
            lrc_text = lrc_text.replace(f'[{match_s}]', replacement)

        # 匹配时间戳
        pattern = r"\[(\d{2}:\d{2}\.\d{2})\]"
        # 进行匹配和替换
        return re.sub(pattern, lambda match: "[" + match.group(1) + "0]", lrc_text)
    else:
        return re.sub(r'[\ufeff\u200b]', '',
                          lrc_text.replace("\r\n", "\n"))
