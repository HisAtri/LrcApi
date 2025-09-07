from fastapi import HTTPException

class LyricsNotFoundError(HTTPException):
    def __init__(self, detail: str = "Lyrics not found"):
        super().__init__(status_code=404, detail=detail)


