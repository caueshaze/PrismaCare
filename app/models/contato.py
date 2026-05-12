from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class Contato(Base):
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(
        Integer,
        ForeignKey("users.id")
    )

    nome = Column(String, nullable=False)

    telefone = Column(String, nullable=False)

    parentesco = Column(String, nullable=False)

    ativo = Column(Boolean, default=True)