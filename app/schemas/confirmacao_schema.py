from typing import Literal, Optional
from pydantic import BaseModel
 
 
# Status válidos para uma confirmação de dose
StatusConfirmacaoLiteral = Literal["PENDENTE", "CONFIRMADO", "NAO_CONFIRMADO", "CANCELADO"]
 
 
class ConfirmacaoCreate(BaseModel):
    id_agendamento: int
    data_hora_prevista: Optional[str] = None
    status: StatusConfirmacaoLiteral = "PENDENTE"
 
 
class ConfirmacaoUpdate(BaseModel):
    status: StatusConfirmacaoLiteral
 
 
class ConfirmacaoResponse(BaseModel):
    id: int
    id_agendamento: int
    data_hora_prevista: Optional[str] = None
    data_hora_confirmacao: Optional[str] = None
    status: StatusConfirmacaoLiteral