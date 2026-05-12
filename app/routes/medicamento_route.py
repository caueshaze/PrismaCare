from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.medicamento import Medicamento
from app.schemas.medicamento_schema import MedicamentoCreate, MedicamentoResponse

router = APIRouter()


@router.post("/medicamentos", response_model=MedicamentoResponse, status_code=201)
def create_medicamento(medicamento: MedicamentoCreate, db: Session = Depends(get_db)):
    novo_medicamento = Medicamento(
        id_usuario=medicamento.id_usuario,
        nome=medicamento.nome,
        dosagem=medicamento.dosagem,
        observacao=medicamento.observacao,
        ativo=medicamento.ativo
    )

    db.add(novo_medicamento)
    db.commit()
    db.refresh(novo_medicamento)

    return novo_medicamento


@router.get("/medicamentos", response_model=list[MedicamentoResponse])
def listar_medicamentos(db: Session = Depends(get_db)):
    return db.query(Medicamento).all()


@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoResponse)
def buscar_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    return medicamento


@router.put("/medicamentos/{medicamento_id}", response_model=MedicamentoResponse)
def atualizar_medicamento(
    medicamento_id: int,
    medicamento_atualizado: MedicamentoCreate,
    db: Session = Depends(get_db)
):
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")

    medicamento.nome = medicamento_atualizado.nome
    medicamento.dosagem = medicamento_atualizado.dosagem
    medicamento.observacao = medicamento_atualizado.observacao
    medicamento.ativo = medicamento_atualizado.ativo

    db.commit()
    db.refresh(medicamento)

    return medicamento


@router.delete("/medicamentos/{medicamento_id}")
def deletar_medicamento(medicamento_id: int, db: Session = Depends(get_db)):
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")

    db.delete(medicamento)
    db.commit()
    return {"message": "Medicamento deletado com sucesso"}