import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.lyric import router as lyric_router
from server.cover import router as cover_router
from server.musictag import router as musictag_router
from utils.config import get_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="LrcApi",
    description="歌词 API 服务，支持歌词查询、封面获取、音乐标签管理",
    version="1.0.0"
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(lyric_router, tags=["歌词"])
app.include_router(cover_router, tags=["封面"])
app.include_router(musictag_router, tags=["音乐标签"])


def main():
    """
    程序入口函数
    """
    config = get_config()
    
    logger.info("正在启动服务器")
    logger.info("您可通过爱发电支持我们，爱发电主页 https://afdian.com/a/ghacg")
    
    uvicorn.run(
        "app:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="debug" if config.debug else "info"
    )


if __name__ == "__main__":
    main()

