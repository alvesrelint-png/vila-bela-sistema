"""
Configuração da conexão com o banco.

Ambiente local (padrão): SQLite, via DATABASE_URL=sqlite:///./vila_bela.db
(ver .env.example). Publicação: PostgreSQL via Supabase — a troca é só a
DATABASE_URL, o código deste arquivo não muda entre os dois ambientes.
Ver CLAUDE.md > Stack para a explicação completa.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vila_bela.db")

# SQLite reclama quando a conexão é acessada de threads diferentes, o que
# acontece normalmente com o FastAPI. Postgres não usa (nem precisa d)e
# connect_args, então só incluímos quando for SQLite mesmo.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe declarativa base — todos os modelos em app/models.py herdam dela."""


def get_db():
    """Dependência do FastAPI: abre uma sessão por request e garante o close no final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
