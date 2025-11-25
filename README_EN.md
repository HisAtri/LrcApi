## About this fork

This fork is based on the upstream project **HisAtri/LrcApi**, but specifically incorporates code from:

- The upstream development branch: **`fix/132`**
- The patch addressing NetEase Cloud Music API changes discussed in Issue **#132**

The official master branch (1.6.x) still contains the outdated NetEase `cloudsearch` implementation, which results in:

- 500 Internal Server Error on `/jsonapi`
- TypeErrors such as `string indices must be integers`

This fork merges the updated NetEase API logic from the `fix/132` branch, enhances it further for Docker runtime stability, and packages it into a working Docker image (`1.6-fix1`).

All original code belongs to the upstream author; this fork only applies compatibility fixes and remains licensed under **GPL-3.0**.

<div align="center">
    <img alt="LOGO" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/LrcAPI-Text-Extra.png" width="313" height="400" />
</div>

# LrcApi

A Flask API For [StreamMusic](https://github.com/gitbobobo/StreamMusic)

> Welcome more music services to integrate with this API, and frontend developers are welcome to propose new API adaptation requirements.

> [JetBrains](https://www.jetbrains.com/) provides free open-source licenses for this project.

<p align="center">
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10|3.11|3.12-blue.svg" alt=""></a>
    <a href="https://hub.docker.com/r/hisatri/lrcapi"><img src="https://img.shields.io/badge/Docker-Quick%20Start-0077ED.svg" alt=""></a>
    <br>
    <img src="https://img.shields.io/github/license/HisAtri/LrcApi?color=%23f280bf" alt="">
    <img src="https://img.shields.io/github/commit-activity/m/HisAtri/LrcApi?color=%23bf4215" alt="">
    <img src="https://img.shields.io/github/stars/HisAtri/LrcApi?style=social" alt="">
</p>

<div align="center">
    <a href="README.md">中文</a> | <a href="README_EN.md">English</a>
</div>

## Features

Supports fetching LRC lyrics via Kugou/Aggregated API

Supports text/json API

Supports fetching music/album/artist covers

Listens on port 28883 by default, API address `http://0.0.0.0:28883/lyrics`; new API address `http://0.0.0.0:28883/jsonapi`; cover API address `http://0.0.0.0:28883/cover`.

### Startup Parameters

| Parameter | Type | Default Value |
| --------- | ---- | ------------- |
| `--port`  | int  | 28883         |
| `--auth`  | str  |               |

The `--auth` parameter is used for header authentication. If left empty, authentication is skipped. It verifies the `Authorization` or `Authentication` field in the header. If authentication fails, a 403 response is returned.

You can also define it using the environment variable `API_AUTH`, which has lower priority than the `--auth` parameter but is easier to deploy in Docker. `-e API_AUTH=custom_auth_key`

## Usage

### Public API

If private deployment is not possible, you can try using the public API first. Note: The public API fetches lyrics via Kugou and other interfaces, which may be slow and not entirely accurate.

Lyrics API address: `https://api.lrc.cx/lyrics`

Cover API address: `https://api.lrc.cx/cover`

### Binary File

Upload to the runtime directory, `./lrcapi --port 8080 --auth custom_auth_key`

### Python Source File

Pull this project; or download and upload to the runtime directory, then unzip the tar.gz

Install dependencies: `pip install -r requirements.txt`

Start the service: `python3 app.py --port 8080 --auth custom_auth_key`

### Docker Deployment

```bash
docker run -d \
    -p 28883:28883 \
    -v /home/user/music:/music \
    -e API_AUTH=custom_auth_key \
    hisatri/lrcapi:latest
```

Alternatively, specify a tag (recommended)

```bash
docker run -d \
    -p 28883:28883 \
    -v /home/user/music:/music \
    -e API_AUTH=custom_auth_key \
    hisatri/lrcapi:1.5.2
```

A Docker-compose configuration is as follows

```yaml
services:
  lrcapi:
    image: hisatri/lrcapi:latest
    container_name: lrcapi
    ports:
      - "28883:28883"
    volumes:
      - /home/user/music:/music
    environment:
      - API_AUTH=custom_auth_key
    restart: always
```

If you are using Navidrome Docker, modify `/home/user/music:/music` to the host path you mapped in Navidrome;

In other words, keep the `-v` parameter consistent with Navidrome.

If you are using Navidrome, map your music file directory to the Docker internal directory; for example, if your music storage directory is `/www/path/music`, modify the mapping in the startup command to `/www/path/music:/www/path/music`

Then access `http://0.0.0.0:28883/lyrics` or the new API `http://0.0.0.0:28883/jsonapi`

The image API address is `http://0.0.0.0:28883/cover`

Note: Image returns currently use a reverse proxy strategy, which may incur some upstream and downstream traffic consumption and latency.

Supports reverse proxy and SSL using Nginx or Apache.

## Music Metadata Modification Interface

### Interface Details

- Request Method: POST
- Request Path: /tag
- Data Type: application/json

### Supported Formats

Tested:

- FLAC(flac)
- ID3v2(mp3)
- VorbisComment(ogg)

### Supported Tags

- title
- artist
- album
- lyrics

### Status Codes

- 200 Success
- 404 File not found
- 421 No permission
- 422 Parsing error
- 5xx Execution error

### Simple Test Environment

```python
import requests
json_data = {
    "path": "/path/to/music/file",
    "title": "title",
    "artist": "artist",
    "album": "album",
    "lyrics": "lyrics"
}
url = 'http://127.0.0.1:28883/tag'
response = requests.post(url, json=json_data)
print(response.status_code)
print(response.text)
```

## Secondary Development Instructions

This program is based on the GPL-3.0 open-source license, and you are free to use, modify, and distribute this program. When developing secondary versions, please comply with the following requirements:

1. Retain the original copyright and license notices in your derivative works.
2. If you have modified this program, clearly state your modifications.
3. When distributing, you need to provide the complete source code and distribute your derivative works under the GPL-3.0 license.
4. Any commercial use based on this program needs to comply with the GPL-3.0 license and remain freely accessible.
5. Other parts of this project (including logos, services, or slogans, etc.) are not open-sourced under the GPL 3.0 agreement.

Ensure you fully understand the requirements of the GPL-3.0 license and comply with the relevant regulations.

# Appreciation

WeChat

<img alt="reward" class="rounded" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/qrcode.png" width="512" height="512" />

[![Star History Chart](https://api.star-history.com/svg?repos=HisAtri/LrcApi&type=Date)](https://star-history.com/#HisAtri/LrcApi&Date)
