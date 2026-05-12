from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.contato import Contato
from app.schemas.contato_schema import ContatoCreate, ContatoResponse

router = APIRouter()


@router.post("/contatos", response_model=ContatoResponse, status_code=201)
def create_contato(contato: ContatoCreate, db: Session = Depends(get_db)):
    novo_contato = Contato(
        id_usuario=contato.id_usuario,
        nome=contato.nome,
        telefone=contato.telefone,
        parentesco=contato.parentesco,
        ativo=contato.ativo
    )

    db.add(novo_contato)
    db.commit()
    db.refresh(novo_contato)

    return novo_contato


@router.get("/contatos", response_model=list[ContatoResponse])
def listar_contatos(db: Session = Depends(get_db)):
    return db.query(Contato).all()


@router.get("/contatos/{contato_id}", response_model=ContatoResponse)
def buscar_contato(contato_id: int, db: Session = Depends(get_db)):
    contato = db.query(Contato).filter(Contato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    return contato


@router.delete("/contatos/{contato_id}")
def deletar_contato(contato_id: int, db: Session = Depends(get_db)):
    contato = db.query(Contato).filter(Contato.id == contato_id).first()
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    db.delete(contato)
    db.commit()
    return {"message": "Contato deletado com sucesso"}