from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True)

    id_usuario = Column(Integer, ForeignKey("users.id"))

    nome = Column(String, nullable=False)
    dosagem = Column(String, nullable=False)

    observacao = Column(String)

    ativo = Column(Boolean, default=True)