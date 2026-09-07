"""
Rotas de pedidos e atendimentos (Sprint 2).

- POST   /mesas/{codigo}/pedidos     criar pedido: abre o atendimento da mesa
         se não houver um aberto, revalida e reserva estoque de cada item numa
         única transação (regra de domínio 4), congela o preço de cada item
         pedido (regra de domínio 6).
- GET    /mesas/{codigo}/pedidos     pedidos do atendimento aberto da mesa
- GET    /pedidos                    fila operacional (filtro por situação)
- PATCH  /pedidos/{id}/situacao      avança a fila (recebido -> em_preparo ->
         pronto -> entregue)
- PATCH  /pedidos/{id}/cancelar      cancela e restaura só a reserva daquele
         pedido (regra de domínio 5)
- GET    /atendimentos               lista atendimentos (filtro aberto/fechado)
- PATCH  /atendimentos/{id}/fechar   fecha a conta, registrando a forma de
         pagamento informada — não processa pagamento de verdade, isso
         continua acontecendo fora do sistema (ver CLAUDE.md > Stack)
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.auth import exigir_admin
from app.services import estoque as servico_estoque

router = APIRouter(tags=["pedidos"])


def _atendimento_aberto_da_mesa(db: Session, mesa: models.Mesa) -> models.Atendimento:
    """Devolve o atendimento aberto da mesa, abrindo um novo se não houver —
    uma sentada = um atendimento; abre sozinho no 1º pedido da mesa."""
    atendimento = (
        db.query(models.Atendimento)
        .filter(
            models.Atendimento.mesa_id == mesa.id,
            models.Atendimento.situacao == models.SituacaoAtendimento.ABERTO,
        )
        .order_by(models.Atendimento.aberto_em.desc())
        .first()
    )
    if atendimento is not None:
        return atendimento

    atendimento = models.Atendimento(mesa_id=mesa.id)
    db.add(atendimento)
    db.flush()
    return atendimento


def _recalcular_valor_atendimento(atendimento: models.Atendimento) -> None:
    """Soma os pedidos não cancelados — um pedido cancelado mantém seu
    valor_total histórico (regra de domínio 6: nunca reescrever o que já
    aconteceu), só deixa de contar para o total da conta."""
    atendimento.valor_total = sum(
        pedido.valor_total
        for pedido in atendimento.pedidos
        if pedido.situacao != models.SituacaoPedido.CANCELADO
    )


# ---------------------------------------------------------------------------
# Pedidos
# ---------------------------------------------------------------------------


@router.post(
    "/mesas/{codigo}/pedidos",
    response_model=schemas.PedidoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_pedido(codigo: str, dados: schemas.PedidoCreate, db: Session = Depends(get_db)):
    mesa = (
        db.query(models.Mesa)
        .filter(models.Mesa.codigo == codigo, models.Mesa.ativa.is_(True))
        .first()
    )
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa não encontrada ou inativa")

    atendimento = _atendimento_aberto_da_mesa(db, mesa)

    pedido = models.Pedido(atendimento_id=atendimento.id)
    db.add(pedido)
    db.flush()

    valor_total_pedido = 0
    for item_dado in dados.itens:
        item_cardapio = db.get(models.ItemCardapio, item_dado.item_id)
        if item_cardapio is None or not item_cardapio.ativo:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Item #{item_dado.item_id} não encontrado ou inativo",
            )

        item_pedido = models.ItemPedido(
            pedido_id=pedido.id,
            item_id=item_cardapio.id,
            quantidade=item_dado.quantidade,
            preco_registrado=item_cardapio.preco,  # regra de domínio 6: congela aqui
            observacao=item_dado.observacao,
        )
        db.add(item_pedido)
        db.flush()

        try:
            servico_estoque.reservar_ingredientes(db, item_pedido)
        except servico_estoque.EstoqueInsuficiente as erro:
            # regra de domínio 4: revalidar e reservar numa única operação —
            # se qualquer item da comanda não tem estoque, o pedido inteiro
            # (e as reservas já feitas para os itens anteriores dele) é
            # desfeito, não só o item que faltou.
            db.rollback()
            raise HTTPException(status_code=409, detail=str(erro)) from erro

        valor_total_pedido += item_cardapio.preco * item_dado.quantidade

    pedido.valor_total = valor_total_pedido
    _recalcular_valor_atendimento(atendimento)

    db.commit()
    db.refresh(pedido)
    return pedido


@router.get("/mesas/{codigo}/pedidos", response_model=list[schemas.PedidoRead])
def pedidos_da_mesa(codigo: str, db: Session = Depends(get_db)):
    """Pedidos do atendimento ABERTO da mesa — é o que o cliente acompanha
    (Sprint 2, tela de acompanhamento) e o que o operador vê ao fechar a conta."""
    mesa = db.query(models.Mesa).filter(models.Mesa.codigo == codigo).first()
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    atendimento = (
        db.query(models.Atendimento)
        .filter(
            models.Atendimento.mesa_id == mesa.id,
            models.Atendimento.situacao == models.SituacaoAtendimento.ABERTO,
        )
        .order_by(models.Atendimento.aberto_em.desc())
        .first()
    )
    if atendimento is None:
        return []

    return (
        db.query(models.Pedido)
        .filter(models.Pedido.atendimento_id == atendimento.id)
        .order_by(models.Pedido.criado_em)
        .all()
    )


@router.get(
    "/pedidos", response_model=list[schemas.PedidoRead], dependencies=[Depends(exigir_admin)]
)
def fila_pedidos(situacao: models.SituacaoPedido | None = None, db: Session = Depends(get_db)):
    """Fila operacional (painel Kanban). Sem filtro, mostra tudo que ainda
    está em andamento (esconde cancelados, mas não esconde entregues — quem
    quiser só os ativos filtra por situacao=recebido/em_preparo/pronto)."""
    query = db.query(models.Pedido)
    if situacao is not None:
        query = query.filter(models.Pedido.situacao == situacao)
    else:
        query = query.filter(models.Pedido.situacao != models.SituacaoPedido.CANCELADO)
    return query.order_by(models.Pedido.criado_em).all()


@router.patch(
    "/pedidos/{pedido_id}/situacao",
    response_model=schemas.PedidoRead,
    dependencies=[Depends(exigir_admin)],
)
def avancar_situacao(
    pedido_id: int, dados: schemas.AtualizarSituacaoPedido, db: Session = Depends(get_db)
):
    pedido = db.get(models.Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.situacao == models.SituacaoPedido.CANCELADO:
        raise HTTPException(status_code=409, detail="Pedido cancelado não pode mudar de situação")
    if dados.situacao == models.SituacaoPedido.CANCELADO:
        raise HTTPException(status_code=400, detail="Use PATCH /pedidos/{id}/cancelar para cancelar")

    pedido.situacao = dados.situacao
    db.commit()
    db.refresh(pedido)
    return pedido


@router.patch(
    "/pedidos/{pedido_id}/cancelar",
    response_model=schemas.PedidoRead,
    dependencies=[Depends(exigir_admin)],
)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Restaura só a reserva deste pedido (regra de domínio 5) — nunca mexe
    no saldo de outros pedidos."""
    pedido = db.get(models.Pedido, pedido_id)
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    if pedido.situacao == models.SituacaoPedido.CANCELADO:
        raise HTTPException(status_code=409, detail="Pedido já está cancelado")

    for item_pedido in pedido.itens:
        servico_estoque.reverter_reserva(db, item_pedido)

    pedido.situacao = models.SituacaoPedido.CANCELADO
    _recalcular_valor_atendimento(pedido.atendimento)

    db.commit()
    db.refresh(pedido)
    return pedido


# ---------------------------------------------------------------------------
# Atendimentos (sessão de mesa)
# ---------------------------------------------------------------------------


@router.get(
    "/atendimentos",
    response_model=list[schemas.AtendimentoRead],
    dependencies=[Depends(exigir_admin)],
)
def listar_atendimentos(
    situacao: models.SituacaoAtendimento | None = None, db: Session = Depends(get_db)
):
    query = db.query(models.Atendimento)
    if situacao is not None:
        query = query.filter(models.Atendimento.situacao == situacao)
    return query.order_by(models.Atendimento.aberto_em.desc()).all()


@router.patch(
    "/atendimentos/{atendimento_id}/fechar",
    response_model=schemas.AtendimentoRead,
    dependencies=[Depends(exigir_admin)],
)
def fechar_atendimento(
    atendimento_id: int, dados: schemas.FecharAtendimento, db: Session = Depends(get_db)
):
    atendimento = db.get(models.Atendimento, atendimento_id)
    if atendimento is None:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado")
    if atendimento.situacao == models.SituacaoAtendimento.FECHADO:
        raise HTTPException(status_code=409, detail="Atendimento já está fechado")

    pedidos_pendentes = [
        p
        for p in atendimento.pedidos
        if p.situacao not in (models.SituacaoPedido.ENTREGUE, models.SituacaoPedido.CANCELADO)
    ]
    if pedidos_pendentes:
        raise HTTPException(
            status_code=409,
            detail="Ainda há pedidos não entregues nesta mesa — entregue ou cancele antes de fechar a conta",
        )

    _recalcular_valor_atendimento(atendimento)
    atendimento.situacao = models.SituacaoAtendimento.FECHADO
    atendimento.fechado_em = datetime.utcnow()
    atendimento.forma_pagamento = dados.forma_pagamento
    atendimento.pago = True

    db.commit()
    db.refresh(atendimento)
    return atendimento
