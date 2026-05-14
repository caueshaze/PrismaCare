from enum import StrEnum


class ConfirmacaoStatus(StrEnum):
    PENDENTE   = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    ATRASADO   = "ATRASADO"
    CANCELADO  = "CANCELADO"


class NotificacaoStatus(StrEnum):
    AGUARDANDO = "AGUARDANDO"
    ENVIADO    = "ENVIADO"
    FALHA      = "FALHA"
