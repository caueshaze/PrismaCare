from enum import Enum
 
 
class StatusConfirmacao(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    NAO_CONFIRMADO = "NAO_CONFIRMADO"
    CANCELADO = "CANCELADO"
 
 
class StatusEnvio(str, Enum):
    AGUARDANDO = "AGUARDANDO"
    ENVIADO = "ENVIADO"
    FALHA = "FALHA"