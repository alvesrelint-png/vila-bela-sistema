"""
Ponto de entrada da API FastAPI.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import models  # noqa: F401  (garante que os modelos sejam registrados na Base)
from app.database import Base, DATABASE_URL, SessionLocal, engine
from app.routers import auth, cardapio, estoque, ingredientes, mesas, pedidos, relatorios

TOTAL_MESAS_SEED = 10


def _migrar_esquema_sqlite() -> None:
    """
    Ajuste mínimo para quem já tinha um vila_bela.db local do Sprint 1:
    `Base.metadata.create_all()` cria TABELAS que ainda não existem, mas não
    adiciona COLUNA nova numa tabela que já existia — e `movimentacoes`
    ganhou `item_pedido_id` no Sprint 2. Sem isso, a reserva de estoque de
    um pedido quebraria com "no such column" no primeiro POST.

    Isto não é migração formal (CLAUDE.md > Convenções gerais reserva isso
    para backend/supabase/migrations/, no Postgres) — é só para o SQLite
    local não ficar preso num estado antigo; roda de graça sempre que a
    coluna já existir.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        colunas = {linha[1] for linha in conn.execute(text("PRAGMA table_info(movimentacoes)"))}
        if colunas and "item_pedido_id" not in colunas:
            conn.execute(text("ALTER TABLE movimentacoes ADD COLUMN item_pedido_id INTEGER"))
            conn.commit()


def _seed_mesas() -> None:
    """Garante 10 mesas cadastradas (codigo "01".."10") na primeira execução
    — pedido explícito da equipe, não precisa de tela de cadastro pra
    começar a usar o sistema."""
    db = SessionLocal()
    try:
        if db.query(models.Mesa).count() > 0:
            return
        for numero in range(1, TOTAL_MESAS_SEED + 1):
            db.add(models.Mesa(codigo=f"{numero:02d}"))
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # SQLite local: cria as tabelas direto a partir dos modelos (sem migração
    # formal). Em Postgres/Supabase, a estrutura nasce de migração versionada
    # em backend/supabase/migrations/ — ver CLAUDE.md > Convenções gerais.
    Base.metadata.create_all(bind=engine)
    _migrar_esquema_sqlite()
    _seed_mesas()
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
app.include_router(mesas.router)
app.include_router(pedidos.router)
app.include_router(relatorios.router)


@app.get("/health")
def health():
    return {"status": "ok"}
