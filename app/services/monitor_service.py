import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from app.database import get_connection
from app.core.constants import NotificacaoStatus
from app.repositories.confirmacao_repo import (
    buscar_candidatas_para_notificacao,
    marcar_como_atrasado,
)
from app.repositories.notificacao_repo import criar_notificacao, notificacao_ja_existe

logger = logging.getLogger("prismacare.monitor")


def varrer_e_notificar() -> dict:
    conn = get_connection()
    try:
        candidatos = buscar_candidatas_para_notificacao(conn)

        alvos: list[tuple[dict, ZoneInfo]] = []
        for c in candidatos:
            raw_tz = c.get("usuario_timezone") or "America/Sao_Paulo"
            try:
                tz = ZoneInfo(raw_tz)
            except ZoneInfoNotFoundError:
                logger.warning(
                    "Timezone inválido no banco para confirmação %s: %r — usando America/Sao_Paulo",
                    c["confirmacao_id"], raw_tz,
                )
                tz = ZoneInfo("America/Sao_Paulo")

            agora_local = datetime.now(tz).replace(tzinfo=None)
            limite_local = agora_local - timedelta(minutes=30)
            prevista = datetime.strptime(c["data_hora_prevista"], "%Y-%m-%d %H:%M:%S")
            if prevista < limite_local:
                alvos.append((c, tz))

        notificacoes_criadas = 0
        confirmacoes_processadas: set[int] = set()

        for alvo, tz in alvos:
            confirmacao_id: int = alvo["confirmacao_id"]
            contato_id: int = alvo["contato_id"]

            if notificacao_ja_existe(conn, confirmacao_id, contato_id):
                continue

            agora_envio = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            criar_notificacao(
                conn,
                id_contato=contato_id,
                id_confirmacao=confirmacao_id,
                data_hora_envio=agora_envio,
                tipo_mensagem="SMS_ALERTA",
                status_envio=NotificacaoStatus.AGUARDANDO,
            )
            notificacoes_criadas += 1
            confirmacoes_processadas.add(confirmacao_id)

        for confirmacao_id in confirmacoes_processadas:
            marcar_como_atrasado(conn, confirmacao_id)

        resultado = {
            "verificadas": len(candidatos),
            "notificacoes_criadas": notificacoes_criadas,
            "confirmacoes_atualizadas": len(confirmacoes_processadas),
        }
        logger.info("Varredura concluída: %s", resultado)
        return resultado
    finally:
        conn.close()
