"""
Autenticação da área administrativa/operacional.

Ambiente local (padrão, Sprint 1): senha única compartilhada, lida de
ADMIN_SENHA no .env (ver .env.example) — o MoSCoW já trata "acesso
administrativo mínimo" como suficiente para essa fase (04 - Backlog e
MVP.md), então não é preciso mais que isso agora.

# TODO (na hora de publicar, ver CLAUDE.md > Stack):
# - Trocar por Supabase Auth: validar o token recebido do frontend em cada
#   rota protegida, em vez da senha única. Trocar só esta camada — o resto
#   do backend não precisa mudar.
"""

import os

from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, status

from app.schemas import LoginRequest, LoginResponse

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(dados: LoginRequest):
    """Recebe a senha, compara com ADMIN_SENHA e devolve um token simples
    (a própria senha) — o frontend guarda esse token e o reenvia como
    `Authorization: Bearer <token>` nas rotas administrativas."""
    admin_senha = os.getenv("ADMIN_SENHA")
    if not admin_senha or dados.senha != admin_senha:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta")
    return LoginResponse(token=admin_senha)


def exigir_admin(authorization: str | None = Header(default=None)) -> None:
    """Dependência que protege rotas administrativas. Espera o header
    `Authorization: Bearer <senha>`."""
    admin_senha = os.getenv("ADMIN_SENHA")
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]

    if not admin_senha or token != admin_senha:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado")
