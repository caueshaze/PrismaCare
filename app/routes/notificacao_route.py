import sqlite3

from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.repositories import notificacao_repo, contato_repo, confirmacao_repo
from app.schemas.notificacao_schema import NotificacaoCreate, NotificacaoResponse
from app.security import obter_usuario_logado

router = APIRouter()


@router.post("/notificacoes", response_model=NotificacaoResponse, status_code=201)
def create_notificacao(
    notificacao: NotificacaoCreate,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    contato = contato_repo.buscar_contato_por_id(conn, notificacao.id_contato)
    if not contato or contato["id_usuario"] != usuario["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado ao contato")

    if not confirmacao_repo.pertence_ao_usuario(conn, notificacao.id_confirmacao, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado à confirmação")

    envio = notificacao.data_hora_envio.isoformat() if notificacao.data_hora_envio else None
    nova = notificacao_repo.criar_notificacao(
        conn,
        id_contato=notificacao.id_contato,
        id_confirmacao=notificacao.id_confirmacao,
        data_hora_envio=envio,
        tipo_mensagem=notificacao.tipo_mensagem,
        status_envio=notificacao.status_envio,
    )
    return nova


@router.get("/notificacoes", response_model=list[NotificacaoResponse])
def listar_notificacoes(
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    return notificacao_repo.listar_notificacoes(conn, id_usuario=usuario["id"])


@router.get("/notificacoes/{notificacao_id}", response_model=NotificacaoResponse)
def buscar_notificacao(
    notificacao_id: int,
    usuario: dict = Depends(obter_usuario_logado),
    conn: sqlite3.Connection = Depends(get_db),
):
    notificacao = notificacao_repo.buscar_notificacao_por_id(conn, notificacao_id)
    if not notificacao:
        raise HTTPException(status_code=404, detail="Notificação não encontrada")
    if not notificacao_repo.pertence_ao_usuario(conn, notificacao_id, usuario["id"]):
        raise HTTPException(status_code=403, detail="Acesso negado")
    return notificacao
