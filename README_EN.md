<div align="center">
    <img alt="LOGO" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/LrcAPI-Text-Extra.png" width="313" height="400" />
</div>

# LrcApi

A Flask API For [StreamMusic](https://github.com/gitbobobo/StreamMusic)

![LrcApi](https://socialify.git.ci/HisAtri/LrcApi/image?description=1&font=Source%20Code%20Pro&forks=1&language=1&name=1&owner=1&pattern=Circuit%20Board&stargazers=1&theme=Light)

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

## Functions

Supports using KuGou API and Multi API to get lyrics.

Supports text/json API

Supports obtaining music/album/artist covers

Default listening on port 28883, with API addresses as follows: API `http://0.0.0.0:28883/lyrics` ；New version API `http://0.0.0.0:28883/jsonapi` ；Cover API `http://0.0.0.0:28883/cover` 。

### Launch Parameters

|   Parameter   |   Type  | Default Value |
| -------- | -------- | -------- |
| `--port`   | int   | 28883   |
| `--auth`  | str   |     |

The `--auth` parameter is used for header authentication. Leave it blank to skip authentication. It validates the `Authorization` or `Authentication` field in the header. If the authentication fails, a 403 response is returned.

Alternatively, you can define the authentication key using the environment variable `API_AUTH`. Its priority is lower than the `--auth` parameter but is more convenient for deployment in Docker. Use `-e API_AUTH=custom_authentication_key`.

## Instructions

### Public API

If private deployment is not possible, you can try using the public API first. Note: The public API obtains lyrics through interfaces such as Kugou, and the response may be slow and not completely accurate.

Lyrics API: `https://api.lrc.cx/lyrics`

CoverAPI: `https://api.lrc.cx/cover`

### Executable File

Upload to the running directory. `./lrcapi --port 8080 --auth {your_privat_key}`

### Python Source File

Pull this project; or download it and upload it to the running directory, and unzip `tar.gz` file.

Install requirements: `pip install -r requirements.txt`

Start the service: `python3 app.py --port 8080 --auth 自定义一个鉴权key`

### Deploy via Docker

```bash
docker run -d -p 28883:28883 -v /home/user/music:/music hisatri/lrcapi:latest
```

Alternatively, you can specify a Tag (recommended)

```bash
docker run -d -p 28883:28883 -v /home/user/music:/music hisatri/lrcapi:alpine-py1.5.2
```

If you are using Navidrome Docker, please modify `/home/user/music:/music` by replacing `/home/user/music` with the host path you have mapped in Navidrome;

In other words, keep the `-v` parameter consistent with the path mapped in Navidrome.

If you are using Navidrome without Docker, map your music directory to the corresponding Docker directory. For example, if your music is stored in `/www/path/music`, modify the mapping in the startup command to `/www/path/music:/www/path/music`.

Then, access `http://0.0.0.0:28883/lyrics` or the new version API `http://0.0.0.0:28883/jsonapi`.

The image API address is `http://0.0.0.0:28883/cover`.

Note: Image retrieval currently employs a reverse proxy strategy, which may result in some upstream and downstream traffic consumption and latency.

You can reverse proxy or SSL encryption through Nginx or Apache.

## API for Modifying Tags

### API Details

- Request Method: POST
- Request Path: /tag
- Data Type: application/json

### Supported Formats

Tested Formats:

- FLAC (flac)
- ID3v2 (mp3)
- VorbisComment (ogg)

### Supported Tags

- Title: title
- Artist: artist
- Album: album
- Lyrics: lyrics

### Status Codes

- 200 Success
- 404 File Not Found
- 421 Unauthorized
- 422 Parsing Error
- 5xx Execution Error

### Simple Testing Environment

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

This program is based on the GPL-3.0 open-source license, and you are free to use, modify, and distribute it at no cost. When engaging in secondary development, please adhere to the following requirements:

1. Retain the original copyright and license statements in your derivative works.
2. Clearly document any modifications you make to this program.
3. When distributing, provide the complete source code and distribute your derivative works under the GPL-3.0 license.
4. Any commercial use based on this program must comply with the GPL-3.0 license and maintain free and open access.
5. Components of this project other than the source code (including logos, services, or slogans) are not open-sourced under the GPL 3.0 license.

Please ensure that you thoroughly understand the requirements of the GPL-3.0 license and comply with relevant provisions.

# Sponsor Me

WeChat

<img alt="reward" class="rounded" src="https://cdn.jsdelivr.net/gh/HisAtri/LrcAPI@main/src/img/qrcode.png" width="512" height="512" />

[![Star History Chart](https://api.star-history.com/svg?repos=HisAtri/LrcApi&type=Date)](https://star-history.com/#HisAtri/LrcApi&Date)
