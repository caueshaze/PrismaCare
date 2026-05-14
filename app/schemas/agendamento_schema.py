from pydantic import BaseModel, field_validator, model_validator
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


class AgendamentoUpdate(BaseModel):
    id_medicamento: Optional[int] = None
    horario: Optional[str] = None
    frequencia: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    ativo: Optional[bool] = None

    @model_validator(mode="after")
    def validar(self):
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Envie pelo menos um campo para atualizar")
        if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
            raise ValueError("data_fim não pode ser anterior a data_inicio")
        return self
