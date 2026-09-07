"""
Rotas de mesas (Sprint 2).

- POST   /mesas                criar mesa
- GET    /mesas                listar mesas com situação (livre/ocupada,
         desde quando e valor já consumido, se ocupada)
- PATCH  /mesas/{id}/desativar nunca DELETE (ver CLAUDE.md)

O seed inicial de 10 mesas (codigo "01".."10") acontece em app/main.py no
startup, não aqui — este router só cuida do CRUD.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.routers.auth import exigir_admin

router = APIRouter(prefix="/mesas", tags=["mesas"])


@router.post(
    "",
    response_model=schemas.MesaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exigir_admin)],
)
def criar_mesa(dados: schemas.MesaCreate, db: Session = Depends(get_db)):
    if db.query(models.Mesa).filter(models.Mesa.codigo == dados.codigo).first():
        raise HTTPException(status_code=409, detail="Já existe uma mesa com este código")

    mesa = models.Mesa(**dados.model_dump())
    db.add(mesa)
    db.commit()
    db.refresh(mesa)
    return mesa


@router.get(
    "",
    response_model=list[schemas.MesaComSituacao],
    dependencies=[Depends(exigir_admin)],
)
def listar_mesas(incluir_inativas: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Mesa)
    if not incluir_inativas:
        query = query.filter(models.Mesa.ativa.is_(True))
    mesas = query.order_by(models.Mesa.codigo).all()

    resultado = []
    for mesa in mesas:
        atendimento = (
            db.query(models.Atendimento)
            .filter(
                models.Atendimento.mesa_id == mesa.id,
                models.Atendimento.situacao == models.SituacaoAtendimento.ABERTO,
            )
            .order_by(models.Atendimento.aberto_em.desc())
            .first()
        )

        base = {
            "id": mesa.id,
            "codigo": mesa.codigo,
            "identificacao": mesa.identificacao,
            "ativa": mesa.ativa,
        }

        if atendimento is None:
            resultado.append(schemas.MesaComSituacao(**base, situacao="livre"))
            continue

        # aberto_em é gravado em UTC (server_default=func.now()); como aqui
        # só precisamos da DURAÇÃO (agora - aberto_em), não do horário
        # absoluto, comparar duas marcas UTC dá o resultado certo sem
        # precisar converter fuso — a conversão só importa para BUCKETING
        # por dia/hora (ver services/relatorios.py).
        minutos_aberta = int((datetime.utcnow() - atendimento.aberto_em).total_seconds() // 60)

        resultado.append(
            schemas.MesaComSituacao(
                **base,
                atendimento_id=atendimento.id,
                situacao="ocupada",
                aberto_em=atendimento.aberto_em,
                minutos_aberta=max(minutos_aberta, 0),
                valor_total=atendimento.valor_total,
            )
        )

    return resultado


@router.patch(
    "/{mesa_id}/desativar",
    response_model=schemas.MesaRead,
    dependencies=[Depends(exigir_admin)],
)
def desativar_mesa(mesa_id: int, db: Session = Depends(get_db)):
    mesa = db.get(models.Mesa, mesa_id)
    if mesa is None:
        raise HTTPException(status_code=404, detail="Mesa não encontrada")

    mesa.ativa = False
    db.commit()
    db.refresh(mesa)
    return mesa
