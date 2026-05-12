from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.database import Base


class Notificacao(Base):
    __tablename__ = "notificacoes"

    id = Column(Integer, primary_key=True, index=True)

    id_contato = Column(
        Integer,
        ForeignKey("contatos.id")
    )

    id_confirmacao = Column(
        Integer,
        ForeignKey("confirmacoes.id")
    )

    data_hora_envio = Column(DateTime)

    tipo_mensagem = Column(String, nullable=False)

    status_envio = Column(String, nullable=False)