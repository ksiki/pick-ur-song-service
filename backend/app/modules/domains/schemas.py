from pydantic import BaseModel, Field, HttpUrl


class ReportBanRequest(BaseModel):
    """Схема отправки отчета о блокировке домена из плеера."""

    url: HttpUrl = Field(..., description="URL домена, который выдал ошибку CORS")


class ReportBanResponse(BaseModel):
    """Схема ответа с новым доменом для перезагрузки плеера."""

    new_url: str = Field(..., description="Новый URL для перезагрузки плеера")
