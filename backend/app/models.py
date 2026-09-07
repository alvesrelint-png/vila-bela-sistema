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
    """

    __tablename__ = "movimentacoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lotes_estoque.id"), nullable=False)
    tipo: Mapped[TipoMovimentacao] = mapped_column(
        Enum(TipoMovimentacao, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )
    quantidade: Mapped[float] = mapped_column(Numeric(12, 3, asdecimal=False), nullable=False)
    motivo: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lote: Mapped["LoteEstoque"] = relationship(back_populates="movimentacoes")


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
# Sprint 2 — Pedido integrado (não implementar antes do Sprint 1 funcionar)
# ---------------------------------------------------------------------------


class Mesa:
    """TODO — campos: id, codigo, identificacao, ativa."""

    __tablename__ = "mesas"


class Pedido:
    """
    TODO — campos: id, mesa_id (FK), situacao, criado_em, valor_total.
    Regra de domínio 4: a criação de um pedido revalida e reserva estoque em
    uma única operação — pensar nisso no service, não só no modelo.
    """

    __tablename__ = "pedidos"


class ItemPedido:
    """
    TODO — campos: id, pedido_id (FK), item_id (FK), quantidade,
    preco_registrado, observacao.
    Regra de domínio 6: preco_registrado é congelado no momento do pedido —
    nunca recalculado a partir de ItemCardapio.preco depois.
    """

    __tablename__ = "itens_pedido"


class UsuarioInterno:
    """TODO — campos: id, nome, acesso (nível/papel), situacao (ativo/inativo).
    Provavelmente delegado ao Supabase Auth em vez de senha própria — ver
    CLAUDE.md > Stack."""

    __tablename__ = "usuarios_internos"
