"""
Relatório de ocupação/rotatividade das mesas.

Não fazia parte do escopo original do MVP (ver docs/planejamento/04 -
Backlog e MVP.md, "Relatórios e indicadores avançados" estava Could/fora do
MVP) — passou a fazer parte com o controle de mesas. Ver a atualização
registrada em 01 e 04.

- GET /relatorios/ocupacao   por dia da semana e por hora do dia: quantos
  atendimentos começaram e quanto entrou de receita (só contas já pagas).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.routers.auth import exigir_admin
from app.services import relatorios as servico_relatorios

router = APIRouter(prefix="/relatorios", tags=["relatorios"])


@router.get(
    "/ocupacao", response_model=schemas.RelatorioOcupacao, dependencies=[Depends(exigir_admin)]
)
def relatorio_ocupacao(db: Session = Depends(get_db)):
    return servico_relatorios.calcular_ocupacao(db)
