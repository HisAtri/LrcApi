import Levenshtein
import math


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


# 分级
def association(text_1: str, text_2: str) -> float:
    """
    通过相对最大匹配距离、相对最小编辑长度（ED）
    测量文本相似度
    以text_1为基准
    权重混合采用x*e^(y-1)
    具体为什么用这个我也不知道
    反正少量实验分离度似乎比算数平均值和几何平均值更好？
    *无所叼胃能用就行
    """
    if text_1 == '':
        return 0.5
    if text_2 == '':
        return 0
    common_ratio = longest_common_substring(text_1, text_2) / len(text_1)
    ed_ratio = Levenshtein.ratio(text_1, text_2)
    similar_ratio = common_ratio * (math.e ** (ed_ratio-1))
    return similar_ratio
