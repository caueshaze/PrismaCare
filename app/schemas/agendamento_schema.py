from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional


class AgendamentoCreate(BaseModel):
    id_medicamento: int
    horario: str
    frequencia: str
    data_inicio: date
    data_fim: Optional[date] = None  # data de fim é opcional
    ativo: bool = True

    @field_validator("data_fim")
    @classmethod
    def data_fim_apos_inicio(cls, v, info):
        if v is not None and "data_inicio" in info.data:
            if v < info.data["data_inicio"]:
                raise ValueError("data_fim não pode ser anterior à data_inicio")
        return v


class AgendamentoResponse(BaseModel):
    id: int
    id_medicamento: int
    horario: str
    frequencia: str
    data_inicio: date
    data_fim: Optional[date] = None
    ativo: bool
