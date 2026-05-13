import sqlite3

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.database import get_db
from app.routes.auth_route import process_login

router = APIRouter()


@router.post("/login")
def login_legacy(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: sqlite3.Connection = Depends(get_db),
):
    # Compat endpoint. Prefer /api/auth/login.
    return process_login(conn, request, form_data.username, form_data.password)
