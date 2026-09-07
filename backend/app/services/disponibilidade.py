"""
Cálculo de disponibilidade — é o coração do Sprint 1 e a hipótese central de
todo o projeto (ver docs/planejamento/01 - Visão do Produto.md).

Importante (regra de domínio 3): a checagem é "E" entre todos os
ingredientes, não "OU" — basta um faltando para bloquear o item inteiro.

Este service deve ser chamado toda vez que o cardápio público for consultado
e toda vez que estoque for alterado (não guardar "disponível" como coluna
fixa que pode ficar desatualizada).
"""

from datetime import date

from sqlalchemy.orm import Session

from app import models


def saldo_disponivel(db: Session, ingrediente_id: int) -> float:
    """Soma apenas os lotes do ingrediente cuja validade ainda não passou
    (regra de domínio 2)."""
    hoje = date.today()
    lotes = (
        db.query(models.LoteEstoque)
        .filter(
            models.LoteEstoque.ingrediente_id == ingrediente_id,
            models.LoteEstoque.validade >= hoje,
        )
        .all()
    )
    return sum(lote.quantidade_atual for lote in lotes)


def item_esta_disponivel(db: Session, item_id: int) -> bool:
    """
    1. Busca o item; se não estiver ativo, retorna False direto.
    2. Busca todas as linhas da ficha técnica do item (ingrediente + quantidade
       necessária).
    3. Para cada ingrediente da ficha, soma apenas os lotes válidos (não vencidos).
    4. Se qualquer ingrediente tiver saldo somado menor que a quantidade
       necessária, o item é indisponível.
    5. Se passou por todos, o item está disponível.
    """
    item = db.get(models.ItemCardapio, item_id)
    if item is None or not item.ativo:
        return False

    ficha = (
        db.query(models.FichaTecnica).filter(models.FichaTecnica.item_id == item_id).all()
    )
    for linha in ficha:
        saldo = saldo_disponivel(db, linha.ingrediente_id)
        if saldo < linha.quantidade_necessaria:
            return False

    return True
