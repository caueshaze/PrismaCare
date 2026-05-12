from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

STATUS_VALIDOS = {"pendente", "confirmado", "nao_confirmado"}


class ConfirmacaoCreate(BaseModel):
    id_agendamento: int
    data_hora_prevista: datetime
    data_hora_confirmacao: Optional[datetime] = None  # pode ser None se ainda não confirmou
    status: str = "pendente"

    @field_validator("status")
    @classmethod
    def status_valido(cls, v):
        if v not in STATUS_VALIDOS:
            raise ValueError(f"Status deve ser um de: {STATUS_VALIDOS}")
        return v


class ConfirmacaoResponse(BaseModel):
    id: int
    id_agendamento: int
    data_hora_prevista: datetime
    data_hora_confirmacao: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True