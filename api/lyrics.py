from mygo.devtools import no_error

from . import *

import os
import re

from flask import request, abort, jsonify
from urllib.parse import unquote_plus
from openai import OpenAI

from mod import lrc
from mod import searchx
from mod import tools
from mod import tag
from mod.auth import require_auth_decorator
from mod.args import args


def read_file_with_encoding(file_path: str, encodings: list[str]):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


@app.route('/lyrics', methods=['GET'], endpoint='lyrics_endpoint')
@v1_bp.route('/lyrics/single', methods=['GET'], endpoint='lyrics_endpoint')
@require_auth_decorator(permission='r')
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def lyrics():
    # 通过request参数获取文件路径
    if not bool(request.args):
        abort(404, "请携带参数访问")
    path = unquote_plus(request.args.get('path', ''))
    # 根据文件路径查找同名的 .lrc 文件
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content: str | None = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                return lrc.standard(file_content)
    try:
        lrc_in = tag.read(path).get("lyrics", "")
        if type(lrc_in) is str and len(lrc_in) > 0:
            return lrc_in
    except:
        pass
    try:
        # 通过request参数获取音乐Tag
        title = unquote_plus(request.args.get('title', ''))
        artist = unquote_plus(request.args.get('artist', ''))
        album = unquote_plus(request.args.get('album', ''))
        result: list = searchx.search_all(title=title, artist=artist, album=album, timeout=30)
        if not result[0].get('lyrics'):
            return "Lyrics not found.", 404
        return result[0].get('lyrics')
    except:
        return "Lyrics not found.", 404


@app.route('/jsonapi', methods=['GET'], endpoint='jsonapi_endpoint')
@v1_bp.route('/lyrics/advance', methods=['GET'], endpoint='jsonapi_endpoint')
@require_auth_decorator(permission='r')
@cache.cached(timeout=86400, key_prefix=make_cache_key)
def lrc_json():
    if not bool(request.args):
        abort(404, "请携带参数访问")
    path = unquote_plus(request.args.get('path', ''))
    title = unquote_plus(request.args.get('title', ''))
    artist = unquote_plus(request.args.get('artist', ''))
    album = unquote_plus(request.args.get('album', ''))
    response = []
    if path:
        lrc_path = os.path.splitext(path)[0] + '.lrc'
        if os.path.isfile(lrc_path):
            file_content = read_file_with_encoding(lrc_path, ['utf-8', 'gbk'])
            if file_content is not None:
                file_content = lrc.standard(file_content)
                response.append({
                    "id": tools.calculate_md5(file_content),
                    "title": title,
                    "artist": artist,
                    "lyrics": file_content
                })

    lyrics_list = searchx.search_all(title, artist, album)
    if lyrics_list:
        for i in lyrics_list:
            if not i:
                continue
            if lyric := i.get('lyrics'):
                i['lyrics'] = lrc.standard(lyric)
                response.append(i)
    _response = jsonify(response)
    _response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return jsonify(response)


@app.route('/translate', methods=['POST'])
@v1_bp.route('/translate', methods=['POST'])
@require_auth_decorator(permission='r')
def lyrics_translate():
    data = request.get_json()
    lyrics = data.get('lyrics')
    BASE_URL = args('ai', 'base_url')
    API_KEY = data.get('token') or args('ai', 'api_key')
    MODEL = args('ai', 'model')

    if not BASE_URL or not API_KEY or not MODEL:
        return jsonify({"error": "Missing required parameters"}), 400
    PROMPT = """You are a lyric translator, tasked with employing exquisite prose to render lines that evoke deep emotions and possess a profound resonance.目标语言是简体中文。

Attention
-保持原文的LRC文本格式；禁止翻译专辑/作者/注释等任何非歌词内容
-不要直接翻译，基于整体进行意译
-结合上下文内容，充分理解歌词中部分词语的隐喻
-注意音韵美
-歌词可能存在重复，请照常翻译，禁止省略。
-**禁止对中文歌词做任何翻译和修改**
-和制汉字不是中文

Use emotional expressions instead of literal translations
Example:
Life's passing by
 - positive：时光匆匆流逝
 - negative：生活在流逝

Contact Context
Example
And after the party's done
I keep on going missing the moments
 - positive：派对过后
 我只顾向前，错过了那些美好时刻
 - negative：派对结束后
 我依然在错过那些瞬间

Example
Caught in a landslide No escape from reality
 - positive：受困在塌方之中，无法逃离**现实**的囚笼
 - negative：被泥石流吞没，无法逃离**真实**

Translation may be interspersed as necessary.
Example:
I'm a Ferrari
Pulled off on Mulholland Drive
 - positive：我就像在穆兰大道上
 疾速飞奔的法拉利
 - negative：我是一辆法拉利
 驶离穆赫兰德大道

Infer the meaning of the statement through context.
Example(Bohemian Rhapsody):
I'm just a poor boy, (oooh, poor boy)
I need no sympathy
**Because I'm easy come, easy go**
**Little high, little low**
 - positive: 因为我总是被人呼来唤去，时而高亢，时而低迷
 - negative: 因为我来去自如，时高时低

理解文化背景下的隐喻
Example
- "I'm gonna tear this city down without you \ I'm goin' Bonnie and Clyde without you"
 - positive：在没有你的城市里纵情徘徊，做孤独的无畏侠客
 - negative：我要在没有你的情况下摧毁这座城市，我要成为没有你的"邦妮与克莱德"
英语国家文化背景：Bonnie 和 Clyde 是美国历史上著名的犯罪情侣，他们在大萧条时期进行了一系列的抢劫和逃亡，象征着反叛和不羁的爱情。
然而，由于翻译的目标语言是简体中文，邦妮与克莱德的典故可能并不容易被理解，因此，更恰当的方式是直接使用比喻义进行翻译，即“做一个孤独且无畏的侠客”

你需要遵守以下思维链：
- Firstly, Infer the country of the author of this song based on the language. Such as [language: en], [language: th], [language: fr], etc.
 - If the language is Chinese, please output [language: zh], ignore all the steps after this, then use [FINAL] tags to enclose the original lyrics and end the translation.
- Next, translate the complete lyrics, encapsulating your LRC format within the [PRE]...[/PRE] tags.
- Then, analyze the emotional undertones of the lyrics and provide a brief overview of their central theme.
- And, assess the shortcomings of the initial translation based on the aforementioned insights.
- Before the final translation, you must ensure that you DID NOT translate any lyrics that are in Chinese. If the Chinese part is translated, please restore it.
- Finally, drawing from this analysis, deliver a refined and high-quality translation of the lyrics, one that remains faithful to the original while evoking deep emotions and possessing poignant resonance, using the [FINAL]...[/FINAL] tags to enclose the ultimate LRC format translation.

**禁止对中文歌词做任何翻译**"""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": lyrics}]
    )
    raw_output = response.choices[0].message.content

    lang_match = re.search(r'\[language:\s*(\w+)\]', raw_output)
    lang_tag = lang_match.group(0) if lang_match else "[language: unknown]"

    # 提取最终翻译
    final_lyric = re.search(r'\[FINAL\](.*?)\[/FINAL\]', raw_output, re.DOTALL)
    if final_lyric:
        extracted = f"[Model Name: {MODEL}]\n" + lang_tag + "\n" + final_lyric.group(1).strip()
        return jsonify({"data": extracted, "status": "success", "raw_output": raw_output})
    else:
        return jsonify({"raw_output": raw_output, "status": "failed"}), 500
