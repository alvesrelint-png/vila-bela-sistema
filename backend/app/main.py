"""
Ponto de entrada da API FastAPI.

Deixado para o Sprint 2: registrar o router de pedidos (app/routers/pedidos.py)
só depois que o Sprint 1 estiver funcionando de ponta a ponta — ver a ordem
de implementação no CLAUDE.md da raiz do repositório.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (garante que os modelos sejam registrados na Base)
from app.database import Base, engine
from app.routers import auth, cardapio, estoque, ingredientes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # SQLite local: cria as tabelas direto a partir dos modelos (sem migração
    # formal). Em Postgres/Supabase, a estrutura nasce de migração versionada
    # em backend/supabase/migrations/ — ver CLAUDE.md > Convenções gerais.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Vila Bela — Gestão", lifespan=lifespan)

# CORS liberado no MVP local: o frontend (HTML/CSS/JS simples) pode ser
# servido de uma origem diferente do backend durante o desenvolvimento.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingredientes.router)
app.include_router(estoque.router)
app.include_router(cardapio.router)
app.include_router(auth.router)


@app.get("/health")
def health():
    return {"status": "ok"}
