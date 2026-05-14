from pydantic import BaseModel
from datetime import datetime
from typing import Literal

from app.core.constants import NotificacaoStatus


class NotificacaoCreate(BaseModel):
    id_contato: int
    id_confirmacao: int
    data_hora_envio: datetime
    tipo_mensagem: str
    status_envio: Literal["AGUARDANDO", "ENVIADO", "FALHA"] = NotificacaoStatus.AGUARDANDO


class NotificacaoResponse(BaseModel):
    id: int
    id_contato: int
    id_confirmacao: int
    data_hora_envio: datetime
    tipo_mensagem: str
    status_envio: Literal["AGUARDANDO", "ENVIADO", "FALHA"]
