import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.repositories import user_repo
from app.schemas.user_schema import UserCreate, UserResponse
from app.security import hash_senha, obter_usuario_logado

router = APIRouter()


@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, conn: sqlite3.Connection = Depends(get_db)):
    existente = user_repo.buscar_usuario_por_email(conn, user.email)
    if existente:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    data_nasc = str(user.data_nascimento) if user.data_nascimento else None
    novo_user = user_repo.criar_usuario(
        conn,
        nome=user.nome,
        telefone=user.telefone,
        email=user.email,
        senha=hash_senha(user.senha),
        data_nascimento=data_nasc,
    )
    return novo_user


@router.get("/users/me", response_model=UserResponse)
def meu_perfil(usuario: dict = Depends(obter_usuario_logado)):
    return usuario


@router.get("/users", response_model=list[UserResponse])
def listar_users(
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    user = user_repo.buscar_usuario_por_id(conn, usuario["id"])
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return [user]


@router.get("/users/{user_id}", response_model=UserResponse)
def buscar_user(
    user_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    if user_id != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    user = user_repo.buscar_usuario_por_id(conn, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@router.delete("/users/{user_id}")
def deletar_user(
    user_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    if user_id != usuario["id"]:
        raise HTTPException(status_code=403, detail="Você só pode deletar sua própria conta")

    try:
        user_repo.deletar_usuario(conn, user_id)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Usuário possui registros vinculados e não pode ser removido",
        )
    return {"message": "Usuário deletado com sucesso"}
