from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from app.database import Base


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)

    id_medicamento = Column(
        Integer,
        ForeignKey("medicamentos.id")
    )

    horario = Column(String, nullable=False)

    frequencia = Column(String, nullable=False)

    data_inicio = Column(Date)

    data_fim = Column(Date)

    ativo = Column(Boolean, default=True)