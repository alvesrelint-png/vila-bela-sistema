"""
Modelos Pydantic (request/response da API) — Sprint 1.

O schema de leitura pública do ItemCardapio (`ItemCardapioPublico`) inclui o
campo calculado `disponivel: bool`, que vem de
app/services/disponibilidade.py — não é uma coluna do banco.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import FormaPagamento, SituacaoAtendimento, SituacaoPedido, TipoMovimentacao, UnidadeBase

# ---------------------------------------------------------------------------
# Ingrediente
# ---------------------------------------------------------------------------


class IngredienteBase(BaseModel):
    nome: str
    unidade_base: UnidadeBase


class IngredienteCreate(IngredienteBase):
    pass


class IngredienteUpdate(BaseModel):
    nome: str | None = None
    unidade_base: UnidadeBase | None = None


class IngredienteRead(IngredienteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool
    criado_em: datetime


class IngredienteComSaldo(IngredienteRead):
    saldo_disponivel: float


class IngredienteFaltando(BaseModel):
    """Um ingrediente da ficha técnica cujo saldo válido não cobre a
    quantidade necessária — usado para explicar por que um item está
    indisponível (ver docs/planejamento/08 - Wireframes.md > Ficha técnica)."""

    ingrediente_id: int
    nome: str
    saldo_disponivel: float
    quantidade_necessaria: float


class DisponibilidadeItem(BaseModel):
    item_id: int
    disponivel: bool
    ingredientes_faltando: list[IngredienteFaltando]


# ---------------------------------------------------------------------------
# Lote de estoque / movimentação
# ---------------------------------------------------------------------------


class LoteEstoqueCreate(BaseModel):
    quantidade_atual: float = Field(gt=0)
    validade: date


class LoteEstoqueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ingrediente_id: int
    quantidade_atual: float
    validade: date
    data_entrada: datetime


class SaldoIngrediente(BaseModel):
    ingrediente_id: int
    saldo_disponivel: float


class MovimentacaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lote_id: int
    tipo: TipoMovimentacao
    quantidade: float
    motivo: str | None
    data: datetime


# ---------------------------------------------------------------------------
# Categoria
# ---------------------------------------------------------------------------


class CategoriaBase(BaseModel):
    nome: str
    ordem: int = 0


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nome: str | None = None
    ordem: int | None = None
    ativa: bool | None = None


class CategoriaRead(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativa: bool


# ---------------------------------------------------------------------------
# Item do cardápio (administrativo)
# ---------------------------------------------------------------------------


class ItemCardapioBase(BaseModel):
    categoria_id: int
    nome: str
    descricao: str | None = None
    preco: Decimal = Field(gt=0)


class ItemCardapioCreate(ItemCardapioBase):
    pass


class ItemCardapioUpdate(BaseModel):
    categoria_id: int | None = None
    nome: str | None = None
    descricao: str | None = None
    preco: Decimal | None = None
    ativo: bool | None = None


class ItemCardapioRead(ItemCardapioBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativo: bool


# ---------------------------------------------------------------------------
# Ficha técnica
# ---------------------------------------------------------------------------


class FichaTecnicaCreate(BaseModel):
    ingrediente_id: int
    quantidade_necessaria: float = Field(gt=0)


class FichaTecnicaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    ingrediente_id: int
    quantidade_necessaria: float


# ---------------------------------------------------------------------------
# Cardápio público
# ---------------------------------------------------------------------------


class ItemCardapioPublico(BaseModel):
    id: int
    categoria_id: int
    nome: str
    descricao: str | None
    preco: Decimal
    disponivel: bool


# ---------------------------------------------------------------------------
# Mesas e atendimentos (Sprint 2)
# ---------------------------------------------------------------------------


class MesaBase(BaseModel):
    codigo: str
    identificacao: str | None = None


class MesaCreate(MesaBase):
    pass


class MesaRead(MesaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ativa: bool


class MesaComSituacao(MesaRead):
    """Visão operacional de uma mesa: livre ou ocupada e, se ocupada, desde
    quando e quanto já foi consumido — é o que o painel de mesas mostra."""

    atendimento_id: int | None = None
    situacao: str  # "livre" | "ocupada"
    aberto_em: datetime | None = None
    minutos_aberta: int | None = None
    valor_total: float | None = None


class AtendimentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mesa_id: int
    situacao: SituacaoAtendimento
    aberto_em: datetime
    fechado_em: datetime | None
    valor_total: float
    forma_pagamento: FormaPagamento | None
    pago: bool


class FecharAtendimento(BaseModel):
    """Só registro interno do que o operador informou ao fechar a conta —
    não processa pagamento de verdade (ver CLAUDE.md > Stack)."""

    forma_pagamento: FormaPagamento


# ---------------------------------------------------------------------------
# Pedidos (Sprint 2)
# ---------------------------------------------------------------------------


class ItemPedidoCreate(BaseModel):
    item_id: int
    quantidade: int = Field(gt=0)
    observacao: str | None = None


class ItemPedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    quantidade: int
    preco_registrado: Decimal
    observacao: str | None


class PedidoCreate(BaseModel):
    itens: list[ItemPedidoCreate] = Field(min_length=1)


class PedidoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    atendimento_id: int
    situacao: SituacaoPedido
    criado_em: datetime
    valor_total: float
    itens: list[ItemPedidoRead]


class AtualizarSituacaoPedido(BaseModel):
    situacao: SituacaoPedido


# ---------------------------------------------------------------------------
# Relatório de ocupação
# ---------------------------------------------------------------------------


class OcupacaoPorDiaSemana(BaseModel):
    dia_semana: int  # 0 = segunda ... 6 = domingo (python date.weekday())
    nome: str
    atendimentos: int
    receita_total: float
    ticket_medio: float


class OcupacaoPorHora(BaseModel):
    hora: int  # 0-23
    atendimentos: int
    receita_total: float


class RelatorioOcupacao(BaseModel):
    """`atendimentos` conta pela hora/dia em que a mesa ABRIU (aberto_em),
    independente de já ter sido paga. `receita_total` só soma atendimentos
    com pago=True — valor ainda não fechado não é receita realizada."""

    por_dia_semana: list[OcupacaoPorDiaSemana]
    por_hora: list[OcupacaoPorHora]


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    senha: str


class LoginResponse(BaseModel):
    token: str
