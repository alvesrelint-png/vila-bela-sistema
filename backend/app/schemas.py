"""
Modelos Pydantic (request/response da API) — Sprint 1.

O schema de leitura pública do ItemCardapio (`ItemCardapioPublico`) inclui o
campo calculado `disponivel: bool`, que vem de
app/services/disponibilidade.py — não é uma coluna do banco.
"""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import TipoMovimentacao, UnidadeBase

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
# Autenticação
# ---------------------------------------------------------------------------


class LoginRequest(BaseModel):
    senha: str


class LoginResponse(BaseModel):
    token: str
