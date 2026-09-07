"""
Reserva, baixa e reversão de estoque geradas por pedidos (Sprint 2).

Regra de domínio 4: a criação de um pedido revalida e reserva estoque em
uma única operação. Regra de domínio 5: o cancelamento restaura só a
reserva daquele pedido, nunca o saldo todo.

Implementação local (SQLite): a "operação única" é a própria transação do
SQLAlchemy — se qualquer ingrediente da ficha técnica não tiver saldo
suficiente, levantamos EstoqueInsuficiente e quem chamou faz `db.rollback()`,
desfazendo tudo que essa reserva já tinha alterado (e também o pedido/itens
ainda não commitados na mesma transação). Em Postgres esse padrão continua
válido; só vale revisar o nível de isolamento antes de publicar, para
garantir que dois pedidos concorrentes não reservem o mesmo saldo ao mesmo
tempo (ver CLAUDE.md > Stack e > Convenções gerais).
"""

from datetime import date

from sqlalchemy.orm import Session

from app import models


class EstoqueInsuficiente(Exception):
    def __init__(self, ingrediente_nome: str, necessario: float, disponivel: float):
        self.ingrediente_nome = ingrediente_nome
        self.necessario = necessario
        self.disponivel = disponivel
        super().__init__(
            f"Estoque insuficiente de {ingrediente_nome}: "
            f"necessário {necessario}, disponível {disponivel}."
        )


def reservar_ingredientes(db: Session, item_pedido: models.ItemPedido) -> None:
    """
    Para o item do cardápio de `item_pedido`, calcula o total necessário de
    cada ingrediente da ficha técnica (quantidade necessária × quantidade
    pedida) e consome dos lotes válidos, do vencimento mais próximo para o
    mais distante (FIFO por validade — reduz desperdício). Gera uma
    Movimentacao(consumo) por lote tocado, ligada a este item_pedido.

    `item_pedido` precisa já ter `id` (dar `db.flush()` antes de chamar).
    Levanta EstoqueInsuficiente sem commitar nada se faltar qualquer
    ingrediente — quem chama deve dar rollback na sessão inteira, o que
    desfaz tanto as movimentações já geradas nesta chamada quanto o
    pedido/itens ainda pendentes na mesma transação.
    """
    ficha = (
        db.query(models.FichaTecnica)
        .filter(models.FichaTecnica.item_id == item_pedido.item_id)
        .all()
    )

    hoje = date.today()
    for linha in ficha:
        necessario = linha.quantidade_necessaria * item_pedido.quantidade

        lotes = (
            db.query(models.LoteEstoque)
            .filter(
                models.LoteEstoque.ingrediente_id == linha.ingrediente_id,
                models.LoteEstoque.validade >= hoje,
                models.LoteEstoque.quantidade_atual > 0,
            )
            .order_by(models.LoteEstoque.validade.asc())
            .all()
        )

        disponivel = sum(lote.quantidade_atual for lote in lotes)
        if disponivel < necessario:
            raise EstoqueInsuficiente(linha.ingrediente.nome, necessario, disponivel)

        restante = necessario
        for lote in lotes:
            if restante <= 0:
                break
            consumido = min(lote.quantidade_atual, restante)
            lote.quantidade_atual -= consumido
            restante -= consumido

            db.add(
                models.Movimentacao(
                    lote_id=lote.id,
                    item_pedido_id=item_pedido.id,
                    tipo=models.TipoMovimentacao.CONSUMO,
                    quantidade=consumido,
                    motivo=f"Pedido — item #{item_pedido.id}",
                )
            )


def reverter_reserva(db: Session, item_pedido: models.ItemPedido) -> None:
    """Devolve aos mesmos lotes exatamente o que este item_pedido consumiu
    (regra de domínio 5): soma as Movimentacao(consumo) dele e gera
    Movimentacao(reversao) de igual quantidade, incrementando o lote de
    volta — nunca mexe no saldo de outros pedidos."""
    consumos = (
        db.query(models.Movimentacao)
        .filter(
            models.Movimentacao.item_pedido_id == item_pedido.id,
            models.Movimentacao.tipo == models.TipoMovimentacao.CONSUMO,
        )
        .all()
    )
    for consumo in consumos:
        lote = db.get(models.LoteEstoque, consumo.lote_id)
        lote.quantidade_atual += consumo.quantidade
        db.add(
            models.Movimentacao(
                lote_id=lote.id,
                item_pedido_id=item_pedido.id,
                tipo=models.TipoMovimentacao.REVERSAO,
                quantidade=consumo.quantidade,
                motivo=f"Cancelamento — item #{item_pedido.id}",
            )
        )
