from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.security import hash_senha

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verifica se o e-mail já está cadastrado
    existente = db.query(User).filter(User.email == user.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    novo_user = User(
        nome=user.nome,
        telefone=user.telefone,
        email=user.email,
        senha=hash_senha(user.senha),  # senha criptografada antes de salvar
        data_nascimento=user.data_nascimento
    )

    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)

    return novo_user


@router.get("/users", response_model=list[UserResponse])
def listar_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def buscar_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.delete("/users/{user_id}")
def deletar_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    db.delete(user)
    db.commit()
    return {"message": "Usuário deletado com sucesso"}