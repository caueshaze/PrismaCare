import re
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

TELEFONE_REGEX = r"^\+?[\d\s\-\(\)]{8,20}$"

class ContatoCreate(BaseModel):
    nome: str
    telefone: str
    parentesco: str
    ativo: bool = True

    @field_validator("nome", "telefone", "parentesco")
    @classmethod
    def nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Campo não pode ser vazio")
        return v

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, v):
        if not re.match(TELEFONE_REGEX, v.strip()):
            raise ValueError("Formato de telefone inválido")
        return v.strip()


class ContatoResponse(BaseModel):
    id: int
    id_usuario: int
    nome: str
    telefone: str
    parentesco: str
    ativo: bool


class ContatoUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    parentesco: Optional[str] = None

    @model_validator(mode="after")
    def pelo_menos_um_campo(self):
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("Envie pelo menos um campo para atualizar")
        return self

    @field_validator("nome", "parentesco")
    @classmethod
    def nao_pode_ser_vazio(cls, v):
        if v is not None and not str(v).strip():
            raise ValueError("Campo não pode ser vazio")
        return v

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, v):
        if v is None:
            return v
        if not re.match(TELEFONE_REGEX, v.strip()):
            raise ValueError("Formato de telefone inválido")
        return v.strip()
