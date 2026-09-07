"""
Rotas de lotes e movimentações de estoque (Sprint 1).

- POST   /ingredientes/{id}/lotes       registrar lote (quantidade + validade)
- GET    /ingredientes/{id}/lotes       listar lotes do ingrediente
- GET    /ingredientes/{id}/saldo       saldo válido (soma de lotes não vencidos)
- GET    /movimentacoes                 histórico
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.auth import exigir_admin
from app.services import disponibilidade

router = APIRouter(tags=["estoque"])


@router.post(
    "/ingredientes/{ingrediente_id}/lotes",
    response_model=schemas.LoteEstoqueRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def registrar_lote(
    ingrediente_id: int, dados: schemas.LoteEstoqueCreate, db: Session = Depends(get_db)
):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    lote = models.LoteEstoque(ingrediente_id=ingrediente_id, **dados.model_dump())
    db.add(lote)
    db.flush()  # garante lote.id antes de criar a movimentação

    movimentacao = models.Movimentacao(
        lote_id=lote.id,
        tipo=models.TipoMovimentacao.ENTRADA,
        quantidade=lote.quantidade_atual,
        motivo="Entrada de lote",
    )
    db.add(movimentacao)
    db.commit()
    db.refresh(lote)
    return lote


@router.get("/ingredientes/{ingrediente_id}/lotes", response_model=list[schemas.LoteEstoqueRead])
def listar_lotes(ingrediente_id: int, db: Session = Depends(get_db)):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    return (
        db.query(models.LoteEstoque)
        .filter(models.LoteEstoque.ingrediente_id == ingrediente_id)
        .order_by(models.LoteEstoque.validade)
        .all()
    )


@router.get("/ingredientes/{ingrediente_id}/saldo", response_model=schemas.SaldoIngrediente)
def saldo_do_ingrediente(ingrediente_id: int, db: Session = Depends(get_db)):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    saldo = disponibilidade.saldo_disponivel(db, ingrediente_id)
    return schemas.SaldoIngrediente(ingrediente_id=ingrediente_id, saldo_disponivel=saldo)


@router.get(
    "/movimentacoes",
    response_model=list[schemas.MovimentacaoRead],
    dependencies=[Depends(exigir_admin)],
)
def listar_movimentacoes(db: Session = Depends(get_db)):
    return db.query(models.Movimentacao).order_by(models.Movimentacao.data.desc()).all()
