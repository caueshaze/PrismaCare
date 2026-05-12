from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.agendamento import Agendamento
from app.schemas.agendamento_schema import AgendamentoCreate, AgendamentoResponse

router = APIRouter()


@router.post("/agendamentos", response_model=AgendamentoResponse, status_code=201)
def create_agendamento(agendamento: AgendamentoCreate, db: Session = Depends(get_db)):
    novo_agendamento = Agendamento(
        id_medicamento=agendamento.id_medicamento,
        horario=agendamento.horario,
        frequencia=agendamento.frequencia,
        data_inicio=agendamento.data_inicio,
        data_fim=agendamento.data_fim,
        ativo=agendamento.ativo
    )

    db.add(novo_agendamento)
    db.commit()
    db.refresh(novo_agendamento)

    return novo_agendamento


@router.get("/agendamentos", response_model=list[AgendamentoResponse])
def listar_agendamentos(db: Session = Depends(get_db)):
    return db.query(Agendamento).all()


@router.get("/agendamentos/{agendamento_id}", response_model=AgendamentoResponse)
def buscar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return agendamento


@router.delete("/agendamentos/{agendamento_id}")
def deletar_agendamento(agendamento_id: int, db: Session = Depends(get_db)):
    agendamento = db.query(Agendamento).filter(Agendamento.id == agendamento_id).first()
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    db.delete(agendamento)
    db.commit()
    return {"message": "Agendamento deletado com sucesso"}