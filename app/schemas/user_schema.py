from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional


class UserCreate(BaseModel):
    nome: str
    telefone: str
    email: str
    senha: str
    data_nascimento: Optional[date] = None

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, v):
        if not v.strip():
            raise ValueError("Nome não pode ser vazio")
        return v

    @field_validator("email")
    @classmethod
    def email_valido(cls, v):
        if "@" not in v or "." not in v:
            raise ValueError("E-mail inválido")
        return v.lower()

    @field_validator("senha")
    @classmethod
    def senha_minima(cls, v):
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres")
        return v


class UserResponse(BaseModel):
    id: int
    nome: str
    telefone: str
    email: str
    data_nascimento: Optional[date] = None

    class Config:
        from_attributes = True