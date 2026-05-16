from pydantic import BaseModel
from typing import Literal, Optional

from app.core.constants import StatusEnvio


class NotificacaoCreate(BaseModel):
    id_contato: int
    id_confirmacao: int
    data_hora_envio: Optional[str] = None
    tipo_mensagem: str
    status_envio: Literal["AGUARDANDO", "ENVIADO", "FALHA"] = StatusEnvio.AGUARDANDO


class NotificacaoResponse(BaseModel):
    id: int
    id_contato: int
    id_confirmacao: int
    data_hora_envio: Optional[str]
    tipo_mensagem: str
    status_envio: Literal["AGUARDANDO", "ENVIADO", "FALHA"]
