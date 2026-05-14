import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.repositories import contato_repo
from app.schemas.contato_schema import ContatoCreate, ContatoResponse, ContatoUpdate
from app.security import obter_usuario_logado

router = APIRouter()


@router.post("/contatos", response_model=ContatoResponse, status_code=201)
def create_contato(
    contato: ContatoCreate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    novo = contato_repo.criar_contato(
        conn,
        id_usuario=usuario["id"],
        nome=contato.nome,
        telefone=contato.telefone,
        parentesco=contato.parentesco,
        ativo=contato.ativo,
    )
    return novo


@router.get("/contatos", response_model=list[ContatoResponse])
def listar_contatos(
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    return contato_repo.listar_contatos(conn, id_usuario=usuario["id"])


@router.get("/contatos/{contato_id}", response_model=ContatoResponse)
def buscar_contato(
    contato_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    contato = contato_repo.buscar_contato_por_id(conn, contato_id)
    if not contato:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    if contato["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return contato


@router.delete("/contatos/{contato_id}")
def deletar_contato(
    contato_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    existente = contato_repo.buscar_contato_por_id(conn, contato_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    if existente["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        contato_repo.deletar_contato(conn, contato_id)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Contato possui registros vinculados e não pode ser removido",
        )
    return {"message": "Contato deletado com sucesso"}


@router.patch("/contatos/{contato_id}", response_model=ContatoResponse)
def atualizar_contato(
    contato_id: int,
    dados: ContatoUpdate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    existente = contato_repo.buscar_contato_por_id(conn, contato_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Contato não encontrado")
    if not contato_repo.pertence_ao_usuario(conn, contato_id, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return contato_repo.atualizar_contato(
        conn, contato_id,
        nome=dados.nome,
        telefone=dados.telefone,
        parentesco=dados.parentesco,
    )
