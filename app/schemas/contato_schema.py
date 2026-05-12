from pydantic import BaseModel, field_validator


class ContatoCreate(BaseModel):
    id_usuario: int
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


class ContatoResponse(BaseModel):
    id: int
    id_usuario: int
    nome: str
    telefone: str
    parentesco: str
    ativo: bool

    class Config:
        from_attributes = True