import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def enviar_whatsapp_simulado(telefone: str, mensagem: str) -> dict:
    logger.info("[WHATSAPP SIMULADO] Para %s: %s", telefone, mensagem)
    return {
        "status_envio": "ENVIADO",
        "data_hora_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
