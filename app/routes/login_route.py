import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.repositories import user_repo
from app.security import verificar_senha, criar_token

router = APIRouter()


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: sqlite3.Connection = Depends(get_db),
):
    user = user_repo.buscar_usuario_por_email(conn, form_data.username.lower())

    if not user or not verificar_senha(form_data.password, user["senha"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")

    token = criar_token(user["id"], user["email"])

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
        },
    }