from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.security import verificar_senha

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    senha: str


@router.post("/login")
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail
    user = db.query(User).filter(User.email == dados.email.lower()).first()

    # Se não encontrou o usuário ou a senha estiver errada, retorna erro
    if not user or not verificar_senha(dados.senha, user.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    return {
        "message": "Login realizado com sucesso",
        "user": {
            "id": user.id,
            "nome": user.nome,
            "email": user.email
        }
    }