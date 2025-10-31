import re
from mod.ttscn import t2s

"""
本模块算法针对常见音乐标题匹配场景应用，着重分离度和效率。
Levenshtein Distance算法实际表现不佳
目前没有好的轻量nn实现，不考虑上模型
当前数据集R~=0.8
"""


def text_convert(text: str):
    patterns = [
        r"(?<!^)\([^)]+?\)",
        r"(?<!^)（[^)]+?）",
        r"\s+$",  # 句末空格
    ]

    for pattern in patterns:
        text_re = re.sub(pattern, '', text)
        text = text_re if len(text_re) else text
    return text


# 最长匹配字段
def longest_common_substring(str1, str2):
    m = len(str1)
    n = len(str2)
    # 创建二维数组来存储最长匹配长度
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    max_length = 0  # 最长匹配长度
    # 填充dp数组
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > max_length:
                    max_length = dp[i][j]
            else:
                dp[i][j] = 0
    # 返回最长匹配长度
    return max_length


def str_duplicate_rate(str1, str2):
    """
    用于计算重复字符
    """
    set1 = set(str1)
    set2 = set(str2)

    common_characters = set1.intersection(set2)
    total_characters = set1.union(set2)

    similarity_ratio = len(common_characters) / len(total_characters)
    return similarity_ratio


def calculate_duplicate_rate(list_1, list_2):
    """
    用于计算重复词素
    """
    count = 0  # 计数器
    for char in list_1:
        char_sim = []

        # 对每个词素进行association计算
        for char_s in list_2:
            char_sim.append(association(char, char_s))
        count += max(char_sim)
    duplicate_rate = count / len(list_1)  # 计算重复率
    return duplicate_rate


# 分级
def association(text_1: str, text_2: str) -> float:
    """
    通过相对最大匹配距离、相对最小编辑长度（ED）
    测量文本相似度
    最长相似、字符重复结合
    权重混合
    :param text_1: 用户传入文本
    :param text_2: 待比较文本
    :return: 相似度 float: 0~1
    """
    if text_1 == '':
        return 0.5
    if text_2 == '':
        return 0
    text_1 = text_1.lower()
    text_2 = text_2.lower()
    common_ratio = longest_common_substring(text_1, text_2) / len(text_1)
    string_dr = str_duplicate_rate(text_1, text_2)
    similar_ratio = common_ratio * (string_dr ** 0.5) ** (1 / 1.5)
    return similar_ratio


def assoc_artists(text_1: str, text_2: str) -> float:
    if text_1 == "":
        return 0.5
    delimiters = [",", "\\", "&", " ", "+", "|", "、", "，", "/"]    # 使用这些分隔符对artists进行分割
    delimiter_pattern = '|'.join(map(re.escape, delimiters))        # 构建正则表达式（自动转义）
    # 对文本进行繁简转换，使用re分割字符串为列表，并使用list-filter函数去除空项
    text_li_1 = list(filter(None, re.split(delimiter_pattern, t2s(text_1))))
    text_li_2 = list(filter(None, re.split(delimiter_pattern, t2s(text_2))))
    ar_ratio = calculate_duplicate_rate(text_li_1, text_li_2)
    return ar_ratio


def zero_item(text: str) -> str:
    punctuation = "'\"?><:;/!@#$%^&*()_-+=！，。、？“”：；【】{}[]（）()|~·`～［］「」｛｝〖〗『』〈〉«»〔〕‹›〝〞‘’＇＇…＃"
    text = text.replace(" ", "")
    for text_z in text:
        if text_z not in punctuation:
            return text_z
    return text[0] if text else text


if __name__ == "__main__":
    text_s = "aaaa&bbbb&ccccc"
    text_r = "aaaa&ccccc&bbbb"
    print(str_duplicate_rate(text_s, text_r))
