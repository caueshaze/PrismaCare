from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class MedicamentoInfo(BaseModel):
    nome: str
    dosagem: str
    observacao: Optional[str] = None


class DoseHojeResponse(BaseModel):
    confirmacao_id: int
    horario_previsto: datetime
    horario_confirmacao: Optional[datetime] = None
    status: str
    medicamento: MedicamentoInfo