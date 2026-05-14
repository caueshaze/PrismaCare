import logging
from datetime import datetime, timezone

from app.database import get_connection
from app.core.constants import NotificacaoStatus
from app.repositories.confirmacao_repo import (
    buscar_confirmacoes_atrasadas,
    marcar_como_atrasado,
)
from app.repositories.notificacao_repo import criar_notificacao, notificacao_ja_existe

logger = logging.getLogger("prismacare.monitor")


def varrer_e_notificar() -> dict:
    conn = get_connection()
    try:
        alvos = buscar_confirmacoes_atrasadas(conn)
        notificacoes_criadas = 0
        confirmacoes_processadas: set[int] = set()

        agora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        for alvo in alvos:
            confirmacao_id: int = alvo["confirmacao_id"]
            contato_id: int = alvo["contato_id"]

            if notificacao_ja_existe(conn, confirmacao_id, contato_id):
                continue

            criar_notificacao(
                conn,
                id_contato=contato_id,
                id_confirmacao=confirmacao_id,
                data_hora_envio=agora,
                tipo_mensagem="SMS_ALERTA",
                status_envio=NotificacaoStatus.AGUARDANDO,
            )
            notificacoes_criadas += 1
            confirmacoes_processadas.add(confirmacao_id)

        for confirmacao_id in confirmacoes_processadas:
            marcar_como_atrasado(conn, confirmacao_id)

        resultado = {
            "verificadas": len(alvos),
            "notificacoes_criadas": notificacoes_criadas,
            "confirmacoes_atualizadas": len(confirmacoes_processadas),
        }
        logger.info("Varredura concluída: %s", resultado)
        return resultado
    finally:
        conn.close()
