import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.core.audit import audit_event
from app.core.config import settings
from app.core.security_controls import (
    client_ip,
    enforce_login_rate_limit,
    enforce_refresh_rate_limit,
    user_agent,
)
from app.database import get_db
from app.repositories import auth_repo, user_repo
from app.security import extrair_payload, gerar_par_tokens, hash_senha, hash_token, verificar_senha

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class LookupEmailRequest(BaseModel):
    email: str


class RegisterRequest(BaseModel):
    email: str
    password: str


def _auth_response(user: dict, access_token: str, refresh_token: str) -> dict:
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_ttl_min * 60,
        "user": {
            "id": user["id"],
            "nome": user["nome"],
            "email": user["email"],
        },
    }


def _normalize_email(email: str) -> str:
    value = email.lower().strip()
    if "@" not in value or "." not in value:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="E-mail inválido")
    return value


def process_login(
    conn: sqlite3.Connection,
    request: Request,
    username: str,
    password: str,
) -> dict:
    email = username.lower().strip()
    ip = client_ip(request)
    ua = user_agent(request)

    enforce_login_rate_limit(request, email)

    blocked, locked_until = auth_repo.login_bloqueado(conn, email=email, ip=ip)
    if blocked:
        auth_repo.registrar_evento_auth(
            conn,
            event="login_blocked",
            success=False,
            user_id=None,
            email=email,
            ip=ip,
            user_agent=ua,
            reason=f"locked_until={locked_until}",
        )
        audit_event("login_blocked", email=email, ip=ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Conta temporariamente bloqueada por tentativas inválidas",
        )

    user = user_repo.buscar_usuario_por_email(conn, email)
    if not user or not verificar_senha(password, user["senha"]):
        lock = auth_repo.registrar_falha_login(
            conn,
            email=email,
            ip=ip,
            threshold=settings.login_lockout_threshold,
            base_lockout_minutes=settings.login_lockout_minutes,
            max_lockout_minutes=settings.login_lockout_max_minutes,
        )
        auth_repo.registrar_evento_auth(
            conn,
            event="login_failed",
            success=False,
            user_id=user["id"] if user else None,
            email=email,
            ip=ip,
            user_agent=ua,
            reason=f"failed_count={lock['failed_count']}",
        )
        audit_event("login_failed", email=email, ip=ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")

    auth_repo.resetar_falhas_login(conn, email=email, ip=ip)

    access_token, refresh_token, session_id = gerar_par_tokens(user["id"], user["email"])
    refresh_payload = extrair_payload(refresh_token, expected_type="refresh")
    auth_repo.criar_refresh_token(
        conn,
        user_id=user["id"],
        session_id=session_id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.fromtimestamp(refresh_payload["exp"], timezone.utc).isoformat(),
        ip=ip,
        user_agent=ua,
    )
    auth_repo.registrar_evento_auth(
        conn,
        event="login_success",
        success=True,
        user_id=user["id"],
        email=user["email"],
        ip=ip,
        user_agent=ua,
    )
    audit_event("login_success", user_id=user["id"], ip=ip)
    return _auth_response(user, access_token, refresh_token)


@router.post("/lookup-email")
def lookup_email(payload: LookupEmailRequest, conn: sqlite3.Connection = Depends(get_db)):
    email = _normalize_email(payload.email)
    return {"exists": user_repo.buscar_usuario_por_email(conn, email) is not None}


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, conn: sqlite3.Connection = Depends(get_db)):
    email = _normalize_email(payload.email)
    if len(payload.password) < 6:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Senha deve ter pelo menos 6 caracteres")

    existente = user_repo.buscar_usuario_por_email(conn, email)
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")

    novo_user = user_repo.criar_usuario(
        conn,
        nome=None,
        telefone=None,
        email=email,
        senha=hash_senha(payload.password),
        data_nascimento=None,
    )
    return {
        "id": novo_user["id"],
        "email": novo_user["email"],
        "nome": novo_user["nome"],
        "telefone": novo_user["telefone"],
        "timezone_confirmed": bool(novo_user["timezone_confirmed"]),
    }


@router.post("/login")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: sqlite3.Connection = Depends(get_db),
):
    return process_login(conn, request, form_data.username, form_data.password)


@router.post("/refresh")
def refresh_token(
    request: Request,
    payload: RefreshRequest,
    conn: sqlite3.Connection = Depends(get_db),
):
    decoded = extrair_payload(payload.refresh_token, expected_type="refresh")
    user_id = int(decoded["sub"])
    enforce_refresh_rate_limit(request, user_id=user_id)

    token_hash_value = hash_token(payload.refresh_token)
    current = auth_repo.buscar_refresh_token_ativo(conn, token_hash_value)
    if not current:
        auth_repo.registrar_evento_auth(
            conn,
            event="refresh_failed",
            success=False,
            user_id=user_id,
            email=decoded.get("email"),
            ip=client_ip(request),
            user_agent=user_agent(request),
            reason="token_not_active",
        )
        audit_event("refresh_failed", user_id=user_id, reason="token_not_active")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    if decoded.get("sid") != current["session_id"]:
        auth_repo.registrar_evento_auth(
            conn,
            event="refresh_failed",
            success=False,
            user_id=user_id,
            email=decoded.get("email"),
            ip=client_ip(request),
            user_agent=user_agent(request),
            reason="session_mismatch",
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    user = user_repo.buscar_usuario_por_id(conn, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")

    auth_repo.revogar_refresh_token(conn, token_hash_value)

    access_token, refresh_token, session_id = gerar_par_tokens(
        user["id"], user["email"], session_id=current["session_id"]
    )
    refresh_payload = extrair_payload(refresh_token, expected_type="refresh")
    auth_repo.criar_refresh_token(
        conn,
        user_id=user["id"],
        session_id=session_id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.fromtimestamp(refresh_payload["exp"], timezone.utc).isoformat(),
        ip=client_ip(request),
        user_agent=user_agent(request),
    )

    auth_repo.registrar_evento_auth(
        conn,
        event="refresh_success",
        success=True,
        user_id=user["id"],
        email=user["email"],
        ip=client_ip(request),
        user_agent=user_agent(request),
    )
    audit_event("refresh_success", user_id=user["id"])
    return _auth_response(user, access_token, refresh_token)


@router.post("/logout")
def logout(
    request: Request,
    payload: LogoutRequest,
    token: str = Depends(oauth2_scheme),
    conn: sqlite3.Connection = Depends(get_db),
):
    decoded = extrair_payload(token, expected_type="access")
    user_id = int(decoded["sub"])
    session_id = decoded.get("sid")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")

    revoked = auth_repo.revogar_sessao(conn, session_id=session_id, user_id=user_id)
    if payload.refresh_token:
        auth_repo.revogar_refresh_token(conn, hash_token(payload.refresh_token))

    auth_repo.registrar_evento_auth(
        conn,
        event="logout",
        success=True,
        user_id=user_id,
        email=decoded.get("email"),
        ip=client_ip(request),
        user_agent=user_agent(request),
        reason=f"revoked_tokens={revoked}",
    )
    audit_event("logout", user_id=user_id, revoked_tokens=revoked)
    return {"message": "Logout realizado com sucesso"}


@router.post("/logout-all")
def logout_all(
    request: Request,
    token: str = Depends(oauth2_scheme),
    conn: sqlite3.Connection = Depends(get_db),
):
    decoded = extrair_payload(token, expected_type="access")
    user_id = int(decoded["sub"])
    revoked = auth_repo.revogar_todas_sessoes(conn, user_id=user_id)

    auth_repo.registrar_evento_auth(
        conn,
        event="logout_all",
        success=True,
        user_id=user_id,
        email=decoded.get("email"),
        ip=client_ip(request),
        user_agent=user_agent(request),
        reason=f"revoked_tokens={revoked}",
    )
    audit_event("logout_all", user_id=user_id, revoked_tokens=revoked)
    return {"message": "Logout global realizado com sucesso"}
