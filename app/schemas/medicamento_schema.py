from pydantic import BaseModel, field_validator
from typing import Optional


class MedicamentoCreate(BaseModel):
    id_usuario: int
    nome: str
    dosagem: str
    observacao: Optional[str] = None  # campo opcional
    ativo: bool = True

    @field_validator("nome", "dosagem")
    @classmethod
    def nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Campo não pode ser vazio")
        return v


class MedicamentoResponse(BaseModel):
    id: int
    id_usuario: int
    nome: str
    dosagem: str
    observacao: Optional[str] = None
    ativo: bool

    class Config:
        from_attributes = True