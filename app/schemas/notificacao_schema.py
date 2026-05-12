from pydantic import BaseModel, field_validator
from datetime import datetime

STATUS_ENVIO_VALIDOS = {"enviado", "falhou", "pendente"}


class NotificacaoCreate(BaseModel):
    id_contato: int
    id_confirmacao: int
    data_hora_envio: datetime
    tipo_mensagem: str
    status_envio: str = "pendente"

    @field_validator("status_envio")
    @classmethod
    def status_valido(cls, v):
        if v not in STATUS_ENVIO_VALIDOS:
            raise ValueError(f"status_envio deve ser um de: {STATUS_ENVIO_VALIDOS}")
        return v


class NotificacaoResponse(BaseModel):
    id: int
    id_contato: int
    id_confirmacao: int
    data_hora_envio: datetime
    tipo_mensagem: str
    status_envio: str
