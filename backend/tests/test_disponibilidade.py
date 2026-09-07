"""
Testes do critério de aceitação mais importante do Sprint 1 (ver
docs/planejamento/04 - Backlog e MVP.md > Critérios de aceitação):

- Item com todos os ingredientes em saldo suficiente -> disponível.
- Item com um ingrediente em saldo insuficiente -> indisponível.
- Item cujo único lote de um ingrediente está vencido -> indisponível
  (lote vencido não conta, mesmo com quantidade > 0).
- Item inativo -> indisponível mesmo com estoque de sobra.
- Ingrediente com saldo em múltiplos lotes (alguns vencidos, outros não) ->
  soma apenas os não vencidos.
"""

from datetime import date, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services import disponibilidade

ONTEM = date.today() - timedelta(days=1)
AMANHA = date.today() + timedelta(days=1)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _criar_ingrediente(db, nome="farinha"):
    ingrediente = models.Ingrediente(nome=nome, unidade_base=models.UnidadeBase.GRAMA)
    db.add(ingrediente)
    db.flush()
    return ingrediente


def _criar_lote(db, ingrediente, quantidade, validade):
    lote = models.LoteEstoque(
        ingrediente_id=ingrediente.id, quantidade_atual=quantidade, validade=validade
    )
    db.add(lote)
    db.flush()
    return lote


def _criar_item(db, nome="pao de queijo", ativo=True):
    categoria = models.Categoria(nome="Salgados")
    db.add(categoria)
    db.flush()

    item = models.ItemCardapio(
        categoria_id=categoria.id, nome=nome, preco=10, ativo=ativo
    )
    db.add(item)
    db.flush()
    return item


def _adicionar_na_ficha(db, item, ingrediente, quantidade_necessaria):
    ficha = models.FichaTecnica(
        item_id=item.id,
        ingrediente_id=ingrediente.id,
        quantidade_necessaria=quantidade_necessaria,
    )
    db.add(ficha)
    db.flush()
    return ficha


def test_item_disponivel_quando_todos_ingredientes_tem_saldo(db):
    ingrediente = _criar_ingrediente(db)
    _criar_lote(db, ingrediente, quantidade=500, validade=AMANHA)
    item = _criar_item(db)
    _adicionar_na_ficha(db, item, ingrediente, quantidade_necessaria=100)

    assert disponibilidade.item_esta_disponivel(db, item.id) is True


def test_item_indisponivel_quando_um_ingrediente_tem_saldo_insuficiente(db):
    ingrediente_ok = _criar_ingrediente(db, "farinha")
    ingrediente_faltando = _criar_ingrediente(db, "queijo")
    _criar_lote(db, ingrediente_ok, quantidade=500, validade=AMANHA)
    _criar_lote(db, ingrediente_faltando, quantidade=10, validade=AMANHA)

    item = _criar_item(db)
    _adicionar_na_ficha(db, item, ingrediente_ok, quantidade_necessaria=100)
    _adicionar_na_ficha(db, item, ingrediente_faltando, quantidade_necessaria=50)

    assert disponibilidade.item_esta_disponivel(db, item.id) is False


def test_item_indisponivel_quando_unico_lote_esta_vencido(db):
    ingrediente = _criar_ingrediente(db)
    _criar_lote(db, ingrediente, quantidade=500, validade=ONTEM)
    item = _criar_item(db)
    _adicionar_na_ficha(db, item, ingrediente, quantidade_necessaria=100)

    assert disponibilidade.item_esta_disponivel(db, item.id) is False


def test_item_inativo_e_sempre_indisponivel(db):
    ingrediente = _criar_ingrediente(db)
    _criar_lote(db, ingrediente, quantidade=500, validade=AMANHA)
    item = _criar_item(db, ativo=False)
    _adicionar_na_ficha(db, item, ingrediente, quantidade_necessaria=100)

    assert disponibilidade.item_esta_disponivel(db, item.id) is False


def test_saldo_soma_apenas_lotes_nao_vencidos(db):
    ingrediente = _criar_ingrediente(db)
    _criar_lote(db, ingrediente, quantidade=100, validade=ONTEM)
    _criar_lote(db, ingrediente, quantidade=50, validade=AMANHA)
    _criar_lote(db, ingrediente, quantidade=30, validade=AMANHA)

    assert disponibilidade.saldo_disponivel(db, ingrediente.id) == 80
