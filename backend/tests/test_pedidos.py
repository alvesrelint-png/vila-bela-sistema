"""
Testes de reserva, baixa e reversão de estoque geradas por pedidos, e do
relatório de ocupação (Sprint 2).

Regra de domínio 4: a criação de um pedido revalida e reserva estoque em
uma única operação — se faltar qualquer ingrediente, nada é alterado.
Regra de domínio 5: o cancelamento restaura só a reserva daquele pedido.
"""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services import estoque, relatorios

AMANHA = date.today() + timedelta(days=1)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _criar_estoque_basico(db, saldo_ingrediente, quantidade_necessaria):
    """Cria e COMMITA um cenário base (ingrediente com um lote, item com
    ficha técnica, mesa) — representa o que já existia antes do pedido, para
    o teste de rollback poder distinguir "o que já estava lá" de "o que a
    tentativa de pedido tentou criar"."""
    ingrediente = models.Ingrediente(nome="Limao", unidade_base=models.UnidadeBase.UNIDADE)
    db.add(ingrediente)
    db.flush()

    db.add(
        models.LoteEstoque(
            ingrediente_id=ingrediente.id, quantidade_atual=saldo_ingrediente, validade=AMANHA
        )
    )

    categoria = models.Categoria(nome="Bebidas")
    db.add(categoria)
    db.flush()

    item = models.ItemCardapio(categoria_id=categoria.id, nome="Caipirinha", preco=15)
    db.add(item)
    db.flush()

    db.add(
        models.FichaTecnica(
            item_id=item.id,
            ingrediente_id=ingrediente.id,
            quantidade_necessaria=quantidade_necessaria,
        )
    )

    mesa = models.Mesa(codigo="01")
    db.add(mesa)
    db.commit()

    return ingrediente, item, mesa


def _criar_pedido_pendente(db, mesa, item, quantidade):
    """Como o router faz: abre um atendimento e cria o pedido/item — tudo
    ainda não commitado, na mesma transação que vai chamar reservar_ingredientes."""
    atendimento = models.Atendimento(mesa_id=mesa.id)
    db.add(atendimento)
    db.flush()

    pedido = models.Pedido(atendimento_id=atendimento.id)
    db.add(pedido)
    db.flush()

    item_pedido = models.ItemPedido(
        pedido_id=pedido.id, item_id=item.id, quantidade=quantidade, preco_registrado=item.preco
    )
    db.add(item_pedido)
    db.flush()
    return item_pedido


def test_reservar_ingredientes_consome_saldo_e_gera_movimentacao(db):
    ingrediente, item, mesa = _criar_estoque_basico(db, saldo_ingrediente=10, quantidade_necessaria=2)
    item_pedido = _criar_pedido_pendente(db, mesa, item, quantidade=3)  # precisa de 6

    estoque.reservar_ingredientes(db, item_pedido)
    db.commit()

    lote = db.query(models.LoteEstoque).filter_by(ingrediente_id=ingrediente.id).first()
    assert lote.quantidade_atual == 4  # 10 - (2 * 3)

    movimentacoes = db.query(models.Movimentacao).filter_by(item_pedido_id=item_pedido.id).all()
    assert len(movimentacoes) == 1
    assert movimentacoes[0].tipo == models.TipoMovimentacao.CONSUMO
    assert movimentacoes[0].quantidade == 6


def test_reservar_ingredientes_levanta_erro_sem_alterar_nada_quando_falta_saldo(db):
    ingrediente, item, mesa = _criar_estoque_basico(db, saldo_ingrediente=5, quantidade_necessaria=2)
    item_pedido = _criar_pedido_pendente(db, mesa, item, quantidade=3)  # precisa de 6, só há 5

    with pytest.raises(estoque.EstoqueInsuficiente):
        estoque.reservar_ingredientes(db, item_pedido)

    db.rollback()  # é isso que o router faz quando a reserva falha

    lote = db.query(models.LoteEstoque).filter_by(ingrediente_id=ingrediente.id).first()
    assert lote.quantidade_atual == 5  # saldo intacto
    assert db.query(models.Movimentacao).count() == 0
    assert db.query(models.Pedido).count() == 0  # o pedido pendente também foi desfeito


def test_reverter_reserva_restaura_apenas_este_item_pedido(db):
    """Dois pedidos consomem do mesmo ingrediente; cancelar um não pode
    devolver a reserva do outro (regra de domínio 5)."""
    ingrediente, item, mesa = _criar_estoque_basico(db, saldo_ingrediente=10, quantidade_necessaria=2)

    item_pedido_1 = _criar_pedido_pendente(db, mesa, item, quantidade=2)  # consome 4
    estoque.reservar_ingredientes(db, item_pedido_1)
    db.commit()

    item_pedido_2 = _criar_pedido_pendente(db, mesa, item, quantidade=1)  # consome 2
    estoque.reservar_ingredientes(db, item_pedido_2)
    db.commit()

    lote = db.query(models.LoteEstoque).filter_by(ingrediente_id=ingrediente.id).first()
    assert lote.quantidade_atual == 4  # 10 - 4 - 2

    estoque.reverter_reserva(db, item_pedido_1)
    db.commit()

    lote = db.query(models.LoteEstoque).filter_by(ingrediente_id=ingrediente.id).first()
    assert lote.quantidade_atual == 8  # 4 + 4 devolvidos do pedido 1, pedido 2 intocado

    reversoes = (
        db.query(models.Movimentacao)
        .filter_by(item_pedido_id=item_pedido_1.id, tipo=models.TipoMovimentacao.REVERSAO)
        .all()
    )
    assert len(reversoes) == 1
    assert reversoes[0].quantidade == 4


def test_calcular_ocupacao_agrega_por_dia_hora_e_receita_so_conta_pagos(db):
    mesa = models.Mesa(codigo="01")
    db.add(mesa)
    db.flush()

    # 2026-09-07 é uma segunda-feira; 17h UTC = 14h em Palmas (UTC-3).
    aberto_em = datetime(2026, 9, 7, 17, 0, 0)

    db.add(
        models.Atendimento(
            mesa_id=mesa.id,
            situacao=models.SituacaoAtendimento.FECHADO,
            aberto_em=aberto_em,
            fechado_em=aberto_em,
            valor_total=50,
            pago=True,
            forma_pagamento=models.FormaPagamento.DINHEIRO,
        )
    )
    db.add(
        models.Atendimento(
            mesa_id=mesa.id,
            situacao=models.SituacaoAtendimento.ABERTO,
            aberto_em=aberto_em,
            valor_total=30,
            pago=False,  # ainda em aberto: conta como ocupação, não como receita
        )
    )
    db.commit()

    relatorio = relatorios.calcular_ocupacao(db)

    segunda = next(d for d in relatorio.por_dia_semana if d.dia_semana == 0)
    assert segunda.atendimentos == 2
    assert segunda.receita_total == 50.0
    assert segunda.ticket_medio == 50.0  # receita / atendimentos PAGOS (1), não os 2 totais

    hora_14 = next(h for h in relatorio.por_hora if h.hora == 14)
    assert hora_14.atendimentos == 2
    assert hora_14.receita_total == 50.0

    # nenhum outro dia/hora deve ter sido afetado
    assert all(d.atendimentos == 0 for d in relatorio.por_dia_semana if d.dia_semana != 0)
    assert all(h.atendimentos == 0 for h in relatorio.por_hora if h.hora != 14)
