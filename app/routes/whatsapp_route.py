from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security_controls import deny_forbidden
from app.schemas.whatsapp_schema import (
    WhatsAppSendResponse,
    WhatsAppStatusResponse,
    WhatsAppTestSendRequest,
)
from app.security import obter_usuario_logado
from app.services.whatsapp_service import enviar_whatsapp, whatsapp_status

router = APIRouter()


@router.post("/whatsapp/test-send", response_model=WhatsAppSendResponse)
def whatsapp_test_send(
    payload: WhatsAppTestSendRequest,
    _usuario: dict = Depends(obter_usuario_logado),
):
    if not settings.enable_whatsapp_test_endpoint:
        deny_forbidden("Endpoint de teste de WhatsApp desabilitado neste ambiente")
    return enviar_whatsapp(payload.telefone, payload.mensagem)


@router.get("/whatsapp/status", response_model=WhatsAppStatusResponse)
def get_whatsapp_status(_usuario: dict = Depends(obter_usuario_logado)):
    return whatsapp_status()
