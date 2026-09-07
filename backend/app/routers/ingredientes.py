"""
Rotas de ingredientes (Sprint 1).

- POST   /ingredientes            criar ingrediente
- GET    /ingredientes            listar ingredientes (ativos por padrão)
- GET    /ingredientes/{id}       detalhe, incluindo saldo válido calculado
- PATCH  /ingredientes/{id}       editar (nome, unidade_base)
- PATCH  /ingredientes/{id}/desativar   nunca DELETE (ver CLAUDE.md)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.auth import exigir_admin
from app.services import disponibilidade

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


@router.post(
    "",
    response_model=schemas.IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def criar_ingrediente(dados: schemas.IngredienteCreate, db: Session = Depends(get_db)):
    ingrediente = models.Ingrediente(**dados.model_dump())
    db.add(ingrediente)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.get("", response_model=list[schemas.IngredienteRead])
def listar_ingredientes(incluir_inativos: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Ingrediente)
    if not incluir_inativos:
        query = query.filter(models.Ingrediente.ativo.is_(True))
    return query.order_by(models.Ingrediente.nome).all()


@router.get("/{ingrediente_id}", response_model=schemas.IngredienteComSaldo)
def detalhar_ingrediente(ingrediente_id: int, db: Session = Depends(get_db)):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    saldo = disponibilidade.saldo_disponivel(db, ingrediente_id)
    return schemas.IngredienteComSaldo(
        **schemas.IngredienteRead.model_validate(ingrediente).model_dump(),
        saldo_disponivel=saldo,
    )


@router.patch(
    "/{ingrediente_id}",
    response_model=schemas.IngredienteRead,
    dependencies=[Depends(exigir_admin)],
)
def editar_ingrediente(
    ingrediente_id: int, dados: schemas.IngredienteUpdate, db: Session = Depends(get_db)
):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(ingrediente, campo, valor)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@router.patch(
    "/{ingrediente_id}/desativar",
    response_model=schemas.IngredienteRead,
    dependencies=[Depends(exigir_admin)],
)
def desativar_ingrediente(ingrediente_id: int, db: Session = Depends(get_db)):
    ingrediente = db.get(models.Ingrediente, ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    ingrediente.ativo = False
    db.commit()
    db.refresh(ingrediente)
    return ingrediente
