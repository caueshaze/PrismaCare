from fastapi import APIRouter, Depends

from app.security import obter_usuario_logado
from app.services.monitor_service import varrer_e_notificar

router = APIRouter()


@router.post("/monitor/varredura")
def trigger_varredura(_usuario: dict = Depends(obter_usuario_logado)):
    return varrer_e_notificar()
