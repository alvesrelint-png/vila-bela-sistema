"""
Modelos SQLAlchemy — refletem o modelo conceitual definido em
docs/planejamento/05 - Arquitetura e Dados.md.

Convenção de toda tabela (ver CLAUDE.md > Convenções gerais):
- nunca apagar de verdade: usar coluna `ativo` (bool) em vez de DELETE;
- carimbos de data (`criado_em` etc.) com server_default=func.now(), não gerados
  pelo Python, para funcionar mesmo em inserções feitas fora da aplicação.
"""

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UnidadeBase(str, enum.Enum):
    """Regra de domínio 1: cada ingrediente usa uma única unidade base no MVP."""

    UNIDADE = "unidade"
    GRAMA = "grama"
    MILILITRO = "mililitro"


class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    CONSUMO = "consumo"
    AJUSTE = "ajuste"
    REVERSAO = "reversao"


class SituacaoAtendimento(str, enum.Enum):
    ABERTO = "aberto"
    FECHADO = "fechado"


class FormaPagamento(str, enum.Enum):
    """Só registro interno (o que o operador informa ao fechar a conta) — o
    sistema não processa pagamento de verdade, ele continua acontecendo fora
    do sistema (ver CLAUDE.md e docs/planejamento/01 - Visão do Produto.md)."""

    DINHEIRO = "dinheiro"
    CARTAO = "cartao"
    PIX = "pix"
    OUTRO = "outro"


class SituacaoPedido(str, enum.Enum):
    RECEBIDO = "recebido"
    EM_PREPARO = "em_preparo"
    PRONTO = "pronto"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


# ---------------------------------------------------------------------------
# Sprint 1 — Estoque -> Cardápio
# ---------------------------------------------------------------------------


class Ingrediente(Base):
    """Regra de domínio 1: cada ingrediente usa uma única unidade base no MVP."""

    __tablename__ = "ingredientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    unidade_base: Mapped[UnidadeBase] = mapped_column(
        Enum(UnidadeBase, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lotes: Mapped[list["LoteEstoque"]] = relationship(
        back_populates="ingrediente", cascade="all, delete-orphan"
    )
    fichas_tecnicas: Mapped[list["FichaTecnica"]] = relationship(back_populates="ingrediente")


class LoteEstoque(Base):
    """
    Regra de domínio 2: lotes vencidos não entram no saldo disponível — isso é
    responsabilidade da consulta que soma o saldo (app/services/disponibilidade.py),
    não uma coluna aqui.
    """

    __tablename__ = "lotes_estoque"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingredientes.id"), nullable=False)
    quantidade_atual: Mapped[float] = mapped_column(Numeric(12, 3, asdecimal=False), nullable=False)
    validade: Mapped[date] = mapped_column(Date, nullable=False)
    data_entrada: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ingrediente: Mapped["Ingrediente"] = relationship(back_populates="lotes")
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(
        back_populates="lote", cascade="all, delete-orphan"
    )


class Movimentacao(Base):
    """
    Existe para dar histórico e rastreabilidade — nenhuma alteração de saldo
    deve acontecer sem gerar uma linha aqui.

    `item_pedido_id` (Sprint 2, além do que 05 - Arquitetura e Dados.md
    listava originalmente): fica nulo para lançamentos manuais (entrada,
    ajuste), e preenchido quando a movimentação (consumo/reversão) foi gerada
    pela reserva de estoque de um pedido — é assim que o cancelamento sabe
    exatamente quais lotes e quanto devolver (regra de domínio 5: restaurar
    só a reserva daquele pedido).
    """

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes_estoque.id"), nullable=False)
    item_pedido_id: Mapped[int | None] = mapped_column(
        ForeignKey("itens_pedido.id"), nullable=True
    )
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(TipoMovimentacao, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3, asdecimal=False), nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lote: Mapped["LoteEstoque"] = relationship(back_populates="movimentacoes")
    item_pedido: Mapped["ItemPedido | None"] = relationship(back_populates="movimentacoes")


class Categoria(Base):
    """Organiza o cardápio."""

    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    itens: Mapped[list["ItemCardapio"]] = relationship(back_populates="categoria")


class ItemCardapio(Base):
    """preco usa Numeric (não Float) — dinheiro em ponto flutuante acumula erro."""

    __tablename__ = "itens_cardapio"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    categoria: Mapped["Categoria"] = relationship(back_populates="itens")
    ficha_tecnica: Mapped[list["FichaTecnica"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )


class FichaTecnica(Base):
    """
    Regra de domínio 3: um item só fica disponível quando ativo E todos os
    ingredientes desta ficha têm saldo válido suficiente. O cálculo de
    disponibilidade em si mora em app/services/disponibilidade.py, não aqui —
    este é só o modelo de dados.
    """

    __tablename__ = "fichas_tecnicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("itens_cardapio.id"), nullable=False)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingredientes.id"), nullable=False)
    quantidade_necessaria: Mapped[float] = mapped_column(
        Numeric(12, 3, asdecimal=False), nullable=False
    )

    item: Mapped["ItemCardapio"] = relationship(back_populates="ficha_tecnica")
    ingrediente: Mapped["Ingrediente"] = relationship(back_populates="fichas_tecnicas")


# ---------------------------------------------------------------------------
# Sprint 2 — Pedido integrado (mesa, atendimento, pedido, ficha congelada)
# ---------------------------------------------------------------------------


class Mesa(Base):
    """codigo é o identificador visível (o que vai no QR code), ex.: '07'."""

    __tablename__ = "mesas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    identificacao: Mapped[str | None] = mapped_column(String(80), nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    atendimentos: Mapped[list["Atendimento"]] = relationship(back_populates="mesa")


class Atendimento(Base):
    """
    Sessão de ocupação de uma mesa — entidade além das 10 originais de
    05 - Arquitetura e Dados.md (ver a atualização feita nesse arquivo).
    Agrupa um ou mais Pedidos da mesma "sentada": abre sozinho quando o
    primeiro pedido da mesa é criado (nenhum atendimento aberto para ela
    naquele momento) e fecha quando o operador encerra a conta, informando
    a forma de pagamento.

    `pago`/`forma_pagamento` são só registro interno do que o operador
    informou — o sistema não processa pagamento de verdade, isso continua
    acontecendo fora do sistema.
    """

    __tablename__ = "atendimentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mesa_id: Mapped[int] = mapped_column(ForeignKey("mesas.id"), nullable=False)
    situacao: Mapped[SituacaoAtendimento] = mapped_column(
        Enum(SituacaoAtendimento, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=SituacaoAtendimento.ABERTO,
    )
    aberto_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    fechado_em: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    valor_total: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False, default=0
    )
    forma_pagamento: Mapped[FormaPagamento | None] = mapped_column(
        Enum(FormaPagamento, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=True,
    )
    pago: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    mesa: Mapped["Mesa"] = relationship(back_populates="atendimentos")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="atendimento")


class Pedido(Base):
    """
    `atendimento_id` no lugar do `mesa_id` sugerido originalmente em
    05 - Arquitetura e Dados.md — a mesa se chega via atendimento (permite
    várias sentadas da mesma mesa ao longo do dia sem ambiguidade). Ver a
    atualização feita nesse arquivo.

    Regra de domínio 4: a criação de um pedido revalida e reserva estoque em
    uma única operação — a lógica mora em app/services/estoque.py, chamada
    pelo router antes de commitar o pedido.
    """

    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    atendimento_id: Mapped[int] = mapped_column(ForeignKey("atendimentos.id"), nullable=False)
    situacao: Mapped[SituacaoPedido] = mapped_column(
        Enum(SituacaoPedido, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
        default=SituacaoPedido.RECEBIDO,
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    valor_total: Mapped[float] = mapped_column(
        Numeric(10, 2, asdecimal=False), nullable=False, default=0
    )

    atendimento: Mapped["Atendimento"] = relationship(back_populates="pedidos")
    itens: Mapped[list["ItemPedido"]] = relationship(
        back_populates="pedido", cascade="all, delete-orphan"
    )


class ItemPedido(Base):
    """
    Regra de domínio 6: preco_registrado é congelado no momento do pedido —
    nunca recalculado a partir de ItemCardapio.preco depois.
    """

    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedidos.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("itens_cardapio.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_registrado: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)

    pedido: Mapped["Pedido"] = relationship(back_populates="itens")
    item: Mapped["ItemCardapio"] = relationship()
    movimentacoes: Mapped[list["Movimentacao"]] = relationship(back_populates="item_pedido")


class UsuarioInterno:
    """TODO — campos: id, nome, acesso (nível/papel), situacao (ativo/inativo).
    Provavelmente delegado ao Supabase Auth em vez de senha própria — ver
    CLAUDE.md > Stack."""

    __tablename__ = "usuarios_internos"
