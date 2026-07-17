from fastapi import HTTPException, status


class OrderValidationException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class SoundCloudClientError(Exception):
    pass


class JWTNotDictErrot(Exception):
    pass
