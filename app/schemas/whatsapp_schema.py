from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class WhatsAppTestSendRequest(BaseModel):
    telefone: str
    mensagem: str

    @field_validator("telefone", "mensagem")
    @classmethod
    def nao_vazio(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Campo não pode ser vazio")
        return normalized


class WhatsAppSendResponse(BaseModel):
    provider: Literal["simulation", "evolution"]
    status_envio: Literal["AGUARDANDO", "ENVIADO", "FALHA"]
    data_hora_envio: str
    raw_response: Optional[dict | str | None] = None
    error: Optional[str] = None


class WhatsAppStatusResponse(BaseModel):
    provider: Literal["simulation", "evolution"]
    configured: bool
    api_url: Optional[str] = None
    instance_name: Optional[str] = None
    test_endpoint_enabled: bool
