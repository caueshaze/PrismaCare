from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class Confirmacao(Base):
    __tablename__ = "confirmacoes"

    id = Column(Integer, primary_key=True, index=True)

    id_agendamento = Column(
        Integer,
        ForeignKey("agendamentos.id")
    )

    data_hora_prevista = Column(DateTime)

    data_hora_confirmacao = Column(DateTime)

    status = Column(String, nullable=False)