import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.repositories import medicamento_repo
from app.schemas.medicamento_schema import MedicamentoCreate, MedicamentoResponse
from app.security import obter_usuario_logado

router = APIRouter()


@router.post("/medicamentos", response_model=MedicamentoResponse, status_code=201)
def create_medicamento(
    medicamento: MedicamentoCreate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    try:
        novo = medicamento_repo.criar_medicamento(
            conn,
            id_usuario=usuario["id"],
            nome=medicamento.nome,
            dosagem=medicamento.dosagem,
            observacao=medicamento.observacao,
            ativo=medicamento.ativo,
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=422, detail="Referência inválida: usuário não encontrado")
    return novo


@router.get("/medicamentos", response_model=list[MedicamentoResponse])
def listar_medicamentos(
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    return medicamento_repo.listar_medicamentos(conn, id_usuario=usuario["id"])


@router.get("/medicamentos/{medicamento_id}", response_model=MedicamentoResponse)
def buscar_medicamento(
    medicamento_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    medicamento = medicamento_repo.buscar_medicamento_por_id(conn, medicamento_id)
    if not medicamento:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    if medicamento["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return medicamento


@router.put("/medicamentos/{medicamento_id}", response_model=MedicamentoResponse)
def atualizar_medicamento(
    medicamento_id: int,
    medicamento_atualizado: MedicamentoCreate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    existente = medicamento_repo.buscar_medicamento_por_id(conn, medicamento_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    if existente["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    atualizado = medicamento_repo.atualizar_medicamento(
        conn,
        medicamento_id=medicamento_id,
        nome=medicamento_atualizado.nome,
        dosagem=medicamento_atualizado.dosagem,
        observacao=medicamento_atualizado.observacao,
        ativo=medicamento_atualizado.ativo,
    )
    return atualizado


@router.delete("/medicamentos/{medicamento_id}")
def deletar_medicamento(
    medicamento_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    existente = medicamento_repo.buscar_medicamento_por_id(conn, medicamento_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Medicamento não encontrado")
    if existente["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        medicamento_repo.deletar_medicamento(conn, medicamento_id)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Medicamento possui registros vinculados e não pode ser removido",
        )
    return {"message": "Medicamento deletado com sucesso"}
