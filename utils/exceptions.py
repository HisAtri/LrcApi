from fastapi import HTTPException

class LyricsNotFoundError(HTTPException):
    def __init__(self, detail: str = "Lyrics not found"):
        super().__init__(status_code=404, detail=detail)

class CoverImageNotFoundError(HTTPException):
    def __init__(self, detail: str = "Cover image not found"):
        super().__init__(status_code=404, detail=detail)

class MusicFileNotFoundError(HTTPException):
    def __init__(self, detail: str = "Music file not found"):
        super().__init__(status_code=404, detail=detail)

class MusicTagError(HTTPException):
    def __init__(self, detail: str = "Music tag operation failed"):
        super().__init__(status_code=500, detail=detail)

class InsufficientFilePermissionError(HTTPException):
    def __init__(self, detail: str = "Insufficient file permission"):
        super().__init__(status_code=403, detail=detail)

class UnsupportedMetadataTypeError(HTTPException):
    def __init__(self, detail: str = "Unsupported metadata type"):
        super().__init__(status_code=400, detail=detail)

class UnauthorizedRequestError(HTTPException):
    def __init__(self, detail: str = "Unauthorized request"):
        super().__init__(status_code=401, detail=detail)
