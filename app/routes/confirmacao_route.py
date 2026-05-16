import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.core.constants import StatusConfirmacao
from app.database import get_db
from app.repositories import confirmacao_repo, agendamento_repo
from app.schemas.confirmacao_schema import ConfirmacaoCreate, ConfirmacaoResponse
from app.security import obter_usuario_logado

router = APIRouter()


@router.post("/confirmacoes", response_model=ConfirmacaoResponse, status_code=201)
def create_confirmacao(
    confirmacao: ConfirmacaoCreate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    if not agendamento_repo.pertence_ao_usuario(conn, confirmacao.id_agendamento, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado")

    fmt = "%Y-%m-%d %H:%M:%S"
    prevista = confirmacao.data_hora_prevista.strftime(fmt) if confirmacao.data_hora_prevista else None
    confirmada = confirmacao.data_hora_confirmacao.strftime(fmt) if confirmacao.data_hora_confirmacao else None
    nova = confirmacao_repo.criar_confirmacao(
        conn,
        id_agendamento=confirmacao.id_agendamento,
        data_hora_prevista=prevista,
        data_hora_confirmacao=confirmada,
        status=confirmacao.status,
    )
    return nova


@router.get("/confirmacoes", response_model=list[ConfirmacaoResponse])
def listar_confirmacoes(
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    return confirmacao_repo.listar_confirmacoes(conn, id_usuario=usuario["id"])


@router.get("/confirmacoes/{confirmacao_id}", response_model=ConfirmacaoResponse)
def buscar_confirmacao(
    confirmacao_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    confirmacao = confirmacao_repo.buscar_confirmacao_por_id(conn, confirmacao_id)
    if not confirmacao:
        raise HTTPException(status_code=404, detail="Confirmação não encontrada")
    if not confirmacao_repo.pertence_ao_usuario(conn, confirmacao_id, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return confirmacao


@router.put("/confirmacoes/{confirmacao_id}/confirmar", response_model=ConfirmacaoResponse)
def confirmar_uso(
    confirmacao_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    existente = confirmacao_repo.buscar_confirmacao_por_id(conn, confirmacao_id)
    if not existente:
        raise HTTPException(status_code=404, detail="Confirmação não encontrada")
    if not confirmacao_repo.pertence_ao_usuario(conn, confirmacao_id, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado")

    atualizada = confirmacao_repo.atualizar_confirmacao(
        conn,
        confirmacao_id=confirmacao_id,
        status=StatusConfirmacao.CONFIRMADO,
        data_hora_confirmacao=datetime.now(timezone.utc).isoformat(),
    )
    return atualizada
