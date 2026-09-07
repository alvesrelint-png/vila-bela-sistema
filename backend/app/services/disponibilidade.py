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

from app import models, schemas


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


def diagnosticar_disponibilidade(db: Session, item_id: int) -> schemas.DisponibilidadeItem:
    """
    Igual a `item_esta_disponivel`, mas devolve também quais ingredientes
    faltam e por quê (saldo válido vs. quantidade necessária) — é o que a
    tela de ficha técnica precisa para mostrar o motivo do bloqueio (ver
    docs/planejamento/08 - Wireframes.md > Ficha técnica).

    1. Busca o item; se não existir ou não estiver ativo, é indisponível
       direto, sem ingrediente "faltando" específico.
    2. Busca todas as linhas da ficha técnica do item (ingrediente + quantidade
       necessária).
    3. Para cada ingrediente da ficha, soma apenas os lotes válidos (não vencidos).
    4. Todo ingrediente cujo saldo for menor que o necessário entra na lista de
       faltantes — o item só está disponível se a lista ficar vazia (regra de
       domínio 3: é "E" entre todos os ingredientes, não "OU").
    """
    item = db.get(models.ItemCardapio, item_id)
    if item is None or not item.ativo:
        return schemas.DisponibilidadeItem(item_id=item_id, disponivel=False, ingredientes_faltando=[])

    ficha = (
        db.query(models.FichaTecnica).filter(models.FichaTecnica.item_id == item_id).all()
    )
    faltando = []
    for linha in ficha:
        saldo = saldo_disponivel(db, linha.ingrediente_id)
        if saldo < linha.quantidade_necessaria:
            faltando.append(
                schemas.IngredienteFaltando(
                    ingrediente_id=linha.ingrediente_id,
                    nome=linha.ingrediente.nome,
                    saldo_disponivel=saldo,
                    quantidade_necessaria=linha.quantidade_necessaria,
                )
            )

    return schemas.DisponibilidadeItem(
        item_id=item_id, disponivel=not faltando, ingredientes_faltando=faltando
    )


def item_esta_disponivel(db: Session, item_id: int) -> bool:
    """Atalho para quando só o booleano importa (ex.: cardápio público)."""
    return diagnosticar_disponibilidade(db, item_id).disponivel
