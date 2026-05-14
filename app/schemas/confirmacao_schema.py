from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional

from app.core.constants import ConfirmacaoStatus


class ConfirmacaoCreate(BaseModel):
    id_agendamento: int
    data_hora_prevista: datetime
    data_hora_confirmacao: Optional[datetime] = None
    status: Literal["PENDENTE", "CONFIRMADO", "ATRASADO", "CANCELADO"] = ConfirmacaoStatus.PENDENTE


class ConfirmacaoResponse(BaseModel):
    id: int
    id_agendamento: int
    data_hora_prevista: datetime
    data_hora_confirmacao: Optional[datetime] = None
    status: Literal["PENDENTE", "CONFIRMADO", "ATRASADO", "CANCELADO"]
