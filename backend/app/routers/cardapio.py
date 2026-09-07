"""
Rotas de categorias, itens do cardápio e ficha técnica (Sprint 1).

- POST/GET/PATCH  /categorias
- POST/GET/PATCH  /itens                    (cardápio administrativo)
- GET             /itens/{id}/ficha-tecnica
- POST            /itens/{id}/ficha-tecnica  (adicionar ingrediente + quantidade)
- GET             /cardapio                  endpoint PÚBLICO — lista itens
    ativos com o campo calculado `disponivel` (chama
    app/services/disponibilidade.py para cada item, não confia em coluna).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.auth import exigir_admin
from app.services import disponibilidade

router = APIRouter(tags=["cardapio"])


# ---------------------------------------------------------------------------
# Categorias
# ---------------------------------------------------------------------------


@router.post(
    "/categorias",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def criar_categoria(dados: schemas.CategoriaCreate, db: Session = Depends(get_db)):
    categoria = models.Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.get("/categorias", response_model=list[schemas.CategoriaRead])
def listar_categorias(incluir_inativas: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Categoria)
    if not incluir_inativas:
        query = query.filter(models.Categoria.ativa.is_(True))
    return query.order_by(models.Categoria.ordem).all()


@router.patch(
    "/categorias/{categoria_id}",
    response_model=schemas.CategoriaRead,
    dependencies=[Depends(exigir_admin)],
)
def editar_categoria(
    categoria_id: int, dados: schemas.CategoriaUpdate, db: Session = Depends(get_db)
):
    categoria = db.get(models.Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


# ---------------------------------------------------------------------------
# Itens do cardápio (administrativo)
# ---------------------------------------------------------------------------


@router.post(
    "/itens",
    response_model=schemas.ItemCardapioRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def criar_item(dados: schemas.ItemCardapioCreate, db: Session = Depends(get_db)):
    categoria = db.get(models.Categoria, dados.categoria_id)
    if categoria is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    item = models.ItemCardapio(**dados.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get(
    "/itens",
    response_model=list[schemas.ItemCardapioRead],
    dependencies=[Depends(exigir_admin)],
)
def listar_itens(incluir_inativos: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.ItemCardapio)
    if not incluir_inativos:
        query = query.filter(models.ItemCardapio.ativo.is_(True))
    return query.order_by(models.ItemCardapio.nome).all()


@router.patch(
    "/itens/{item_id}",
    response_model=schemas.ItemCardapioRead,
    dependencies=[Depends(exigir_admin)],
)
def editar_item(item_id: int, dados: schemas.ItemCardapioUpdate, db: Session = Depends(get_db)):
    item = db.get(models.ItemCardapio, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if dados.categoria_id is not None and db.get(models.Categoria, dados.categoria_id) is None:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(item, campo, valor)
    db.commit()
    db.refresh(item)
    return item


@router.patch(
    "/itens/{item_id}/desativar",
    response_model=schemas.ItemCardapioRead,
    dependencies=[Depends(exigir_admin)],
)
def desativar_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.ItemCardapio, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    item.ativo = False
    db.commit()
    db.refresh(item)
    return item


# ---------------------------------------------------------------------------
# Ficha técnica
# ---------------------------------------------------------------------------


@router.get("/itens/{item_id}/ficha-tecnica", response_model=list[schemas.FichaTecnicaRead])
def listar_ficha_tecnica(item_id: int, db: Session = Depends(get_db)):
    item = db.get(models.ItemCardapio, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    return (
        db.query(models.FichaTecnica).filter(models.FichaTecnica.item_id == item_id).all()
    )


@router.post(
    "/itens/{item_id}/ficha-tecnica",
    response_model=schemas.FichaTecnicaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def adicionar_ingrediente_na_ficha(
    item_id: int, dados: schemas.FichaTecnicaCreate, db: Session = Depends(get_db)
):
    item = db.get(models.ItemCardapio, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    ingrediente = db.get(models.Ingrediente, dados.ingrediente_id)
    if ingrediente is None:
        raise HTTPException(status_code=404, detail="Ingrediente não encontrado")

    linha = models.FichaTecnica(item_id=item_id, **dados.model_dump())
    db.add(linha)
    db.commit()
    db.refresh(linha)
    return linha


@router.get(
    "/itens/{item_id}/disponibilidade",
    response_model=schemas.DisponibilidadeItem,
    dependencies=[Depends(exigir_admin)],
)
def disponibilidade_do_item(item_id: int, db: Session = Depends(get_db)):
    """Diagnóstico usado pela tela de ficha técnica: além do booleano, diz
    qual ingrediente falta e por quê (saldo válido vs. necessário)."""
    item = db.get(models.ItemCardapio, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    return disponibilidade.diagnosticar_disponibilidade(db, item_id)


# ---------------------------------------------------------------------------
# Cardápio público
# ---------------------------------------------------------------------------


@router.get("/cardapio", response_model=list[schemas.ItemCardapioPublico])
def cardapio_publico(db: Session = Depends(get_db)):
    itens = (
        db.query(models.ItemCardapio)
        .filter(models.ItemCardapio.ativo.is_(True))
        .order_by(models.ItemCardapio.categoria_id, models.ItemCardapio.nome)
        .all()
    )
    return [
        schemas.ItemCardapioPublico(
            id=item.id,
            categoria_id=item.categoria_id,
            nome=item.nome,
            descricao=item.descricao,
            preco=item.preco,
            disponivel=disponibilidade.item_esta_disponivel(db, item.id),
        )
        for item in itens
    ]
