from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.confirmacao import Confirmacao
from app.schemas.confirmacao_schema import ConfirmacaoCreate, ConfirmacaoResponse

router = APIRouter()


@router.post("/confirmacoes", response_model=ConfirmacaoResponse, status_code=201)
def create_confirmacao(confirmacao: ConfirmacaoCreate, db: Session = Depends(get_db)):
    nova_confirmacao = Confirmacao(
        id_agendamento=confirmacao.id_agendamento,
        data_hora_prevista=confirmacao.data_hora_prevista,
        data_hora_confirmacao=confirmacao.data_hora_confirmacao,
        status=confirmacao.status
    )

    db.add(nova_confirmacao)
    db.commit()
    db.refresh(nova_confirmacao)

    return nova_confirmacao


@router.get("/confirmacoes", response_model=list[ConfirmacaoResponse])
def listar_confirmacoes(db: Session = Depends(get_db)):
    return db.query(Confirmacao).all()


@router.get("/confirmacoes/{confirmacao_id}", response_model=ConfirmacaoResponse)
def buscar_confirmacao(confirmacao_id: int, db: Session = Depends(get_db)):
    confirmacao = db.query(Confirmacao).filter(Confirmacao.id == confirmacao_id).first()
    if not confirmacao:
        raise HTTPException(status_code=404, detail="Confirmação não encontrada")
    return confirmacao


@router.put("/confirmacoes/{confirmacao_id}/confirmar", response_model=ConfirmacaoResponse)
def confirmar_uso(confirmacao_id: int, db: Session = Depends(get_db)):
    """Marca uma confirmação como confirmado com o horário atual."""
    from datetime import datetime

    confirmacao = db.query(Confirmacao).filter(Confirmacao.id == confirmacao_id).first()
    if not confirmacao:
        raise HTTPException(status_code=404, detail="Confirmação não encontrada")

    confirmacao.status = "confirmado"
    confirmacao.data_hora_confirmacao = datetime.now()

    db.commit()
    db.refresh(confirmacao)

    return confirmacao