import os

from . import *

from flask import request, render_template_string

from mod import tag
from mod.auth import webui
from mod.auth.authentication import require_auth


@app.route('/tag', methods=['GET', 'POST', 'PUT'])
@v1_bp.route('/tag', methods=['GET', 'POST', 'PUT'])
def setTag():
    def validate_json_structure(data):
        if not isinstance(data, dict):
            return False
        if "path" not in data:
            return False
        return True

    match require_auth(request=request, permission='rw'):
        case -1:
            return render_template_string(webui.error()), 403
        case -2:
            return render_template_string(webui.error()), 421

    musicData = request.json
    if not validate_json_structure(musicData):
        return "Invalid JSON structure.", 422

    audio_path = musicData.get("path")
    if not audio_path:
        return "Missing 'path' key in JSON.", 422

    if not os.path.exists(audio_path):
        return "File not found.", 404

    supported_tags = {
        "tracktitle": {"allow": (str, bool, type(None)), "caption": "Track Title"},
        "artist": {"allow": (str, bool, type(None)), "caption": "Artists"},
        "album": {"allow": (str, bool, type(None)), "caption": "Albums"},
        "year": {"allow": (int, bool, type(None)), "caption": "Album year"},
        "lyrics": {"allow": (str, bool, type(None)), "caption": "Lyrics text"}
    }
    if "title" in musicData and "tracktitle" not in musicData:
        musicData["tracktitle"] = musicData["title"]
    tags_to_set = {}
    for key, value in musicData.items():
        if key in supported_tags and isinstance(value, supported_tags[key]["allow"]):
            tags_to_set[key] = value
    try:
        tag.tin(tags=tags_to_set, file=audio_path)
    except TypeError as e:
        return str(e), 524
    except FileNotFoundError as e:
        return str(e), 404
    except Exception as e:
        return str(e), 500
    return "Succeed", 200
