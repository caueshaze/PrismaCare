from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HistoricoItemResponse(BaseModel):
    confirmacao_id: int
    agendamento_id: int
    medicamento_id: int
    medicamento: str
    dosagem: str
    horario_previsto: datetime
    horario_confirmacao: Optional[datetime] = None
    status: str
