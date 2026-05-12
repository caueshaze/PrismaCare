from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notificacao import Notificacao
from app.schemas.notificacao_schema import NotificacaoCreate, NotificacaoResponse

router = APIRouter()


@router.post("/notificacoes", response_model=NotificacaoResponse, status_code=201)
def create_notificacao(notificacao: NotificacaoCreate, db: Session = Depends(get_db)):
    nova_notificacao = Notificacao(
        id_contato=notificacao.id_contato,
        id_confirmacao=notificacao.id_confirmacao,
        data_hora_envio=notificacao.data_hora_envio,
        tipo_mensagem=notificacao.tipo_mensagem,
        status_envio=notificacao.status_envio
    )

    db.add(nova_notificacao)
    db.commit()
    db.refresh(nova_notificacao)

    return nova_notificacao


@router.get("/notificacoes", response_model=list[NotificacaoResponse])
def listar_notificacoes(db: Session = Depends(get_db)):
    return db.query(Notificacao).all()


@router.get("/notificacoes/{notificacao_id}", response_model=NotificacaoResponse)
def buscar_notificacao(notificacao_id: int, db: Session = Depends(get_db)):
    notificacao = db.query(Notificacao).filter(Notificacao.id == notificacao_id).first()
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    return notificacao