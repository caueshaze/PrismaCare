from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security_controls import deny_forbidden
from app.security import obter_usuario_logado
from app.services.monitor_service import varrer_e_notificar

router = APIRouter()


@router.post("/monitor/varredura")
def trigger_varredura(_usuario: dict = Depends(obter_usuario_logado)):
    if not settings.enable_manual_monitor_endpoint:
        deny_forbidden("Endpoint de varredura manual desabilitado neste ambiente")
    return varrer_e_notificar()
