import os

from . import *

from flask import request, render_template_string, abort

from mod import tag
from mod.auth import webui
from mod.auth.authentication import require_auth
from mod.dev.debugger import debugger


@app.route('/tag', methods=['POST', 'PUT'])
@app.route('/confirm', methods=['POST', 'PUT'])
def set_tag():
    match require_auth(request=request, permission='rw'):
        case -1:
            logger.error("Unauthorized access: 未经授权的用户请求修改标签")
            return render_template_string(webui.error()), 403
        case -2:
            logger.error("Unauthorized access: 您没有为API设置鉴权功能，为了安全起见，有关本地文件修改的功能无法使用。"
                         "具体请查看<https://docs.lrc.cx/docs/deploy/auth>以启用API鉴权功能。")
            return render_template_string(webui.error()), 421

    music_data = request.json
    audio_path = music_data.get("path")
    if not audio_path:
        return "Missing 'path' key in JSON.", 422
    debugger.log("info", f"Editing file {audio_path}")
    if not os.path.exists(audio_path):
        debugger.log("error", f"File not found: {audio_path}")
        return "File not found.", 404
    supported_tags = {
        "tracktitle": {"allow": (str, bool, type(None)), "caption": "Track Title"},
        "artist": {"allow": (str, bool, type(None)), "caption": "Artists"},
        "album": {"allow": (str, bool, type(None)), "caption": "Albums"},
        "year": {"allow": (int, bool, type(None)), "caption": "Album year"},
        "lyrics": {"allow": (str, bool, type(None)), "caption": "Lyrics text"}
    }
    music_data["tracktitle"] = music_data.get("tracktitle") or music_data.get("title")
    tags_to_set = {}
    for key, value in music_data.items():
        if key in supported_tags and isinstance(value, supported_tags[key]["allow"]):
            tags_to_set[key] = value
    try:
        tag.write(tags=tags_to_set, file=audio_path)
    except TypeError as e:
        logger.error(f"TypeError at endpoint /confirm: {str(e)}")
        return {"code": 524, "error": str(e)}, 524
    except FileNotFoundError as e:
        logger.error(f"Error at endpoint /confirm: {audio_path} file not found.")
        return {"code": 404, "error": str(e)}, 404
    except Exception as e:
        logger.error(f"Unknown Error at endpoint /confirm: {str(e)}")
        return {"code": 500, "error": str(e)}, 500
    return {"code": 200, "log": f"Successfully edited file {audio_path}"}, 200
