"""
Relatório de ocupação — não estava no escopo original do MVP
(docs/planejamento/04 - Backlog e MVP.md tinha "Relatórios e indicadores
avançados" marcado Could/fora do MVP), mas passou a ser parte do controle de
mesas pedido pela equipe. Ver a atualização feita em 01 e 04.

Responde duas perguntas operacionais: em que dia da semana / horário mais
gente senta (ocupação), e em que dia entra mais dinheiro (receita).
"""

from collections import defaultdict
from datetime import timedelta

from sqlalchemy.orm import Session

from app import models, schemas

# O banco grava aberto_em em UTC (server_default=func.now(), convenção do
# CLAUDE.md) — mas "que dia da semana"/"que hora" só faz sentido no fuso da
# Vila Bela (Palmas-TO). América/Araguaina é UTC-3 e não observa horário de
# verão desde 2019, então um offset fixo é suficiente (sem depender de
# zoneinfo/pytz só para isso).
OFFSET_HORARIO_LOCAL = timedelta(hours=-3)

NOMES_DIA_SEMANA = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]


def calcular_ocupacao(db: Session) -> schemas.RelatorioOcupacao:
    """
    Agrega todos os atendimentos (de todas as mesas) por dia da semana e por
    hora do dia em que abriram:

    - `atendimentos`: contagem de todos, pagos ou não — é a "ocupação",
      quantas mesas começaram a ser atendidas naquele dia/horário.
    - `receita_total`: soma só dos atendimentos com pago=True — valor ainda
      em aberto não é receita realizada.
    - `ticket_medio` (por dia da semana): receita_total dividida pelo número
      de atendimentos PAGOS (não pelo total), para não subestimar o ticket
      por causa de contas ainda em aberto.

    O bucketing é feito em Python, não em função de data de um dialeto SQL
    específico — mantém o código portável entre SQLite e Postgres (ver
    CLAUDE.md > Stack).
    """
    atendimentos = db.query(models.Atendimento).all()

    contagem_dia: dict[int, int] = defaultdict(int)
    contagem_pagos_dia: dict[int, int] = defaultdict(int)
    receita_dia: dict[int, float] = defaultdict(float)

    contagem_hora: dict[int, int] = defaultdict(int)
    receita_hora: dict[int, float] = defaultdict(float)

    for atendimento in atendimentos:
        aberto_em_local = atendimento.aberto_em + OFFSET_HORARIO_LOCAL
        dia_semana = aberto_em_local.weekday()  # 0 = segunda ... 6 = domingo
        hora = aberto_em_local.hour

        contagem_dia[dia_semana] += 1
        contagem_hora[hora] += 1

        if atendimento.pago:
            contagem_pagos_dia[dia_semana] += 1
            receita_dia[dia_semana] += atendimento.valor_total
            receita_hora[hora] += atendimento.valor_total

    por_dia_semana = [
        schemas.OcupacaoPorDiaSemana(
            dia_semana=dia,
            nome=NOMES_DIA_SEMANA[dia],
            atendimentos=contagem_dia[dia],
            receita_total=round(receita_dia[dia], 2),
            ticket_medio=(
                round(receita_dia[dia] / contagem_pagos_dia[dia], 2)
                if contagem_pagos_dia[dia]
                else 0.0
            ),
        )
        for dia in range(7)
    ]

    por_hora = [
        schemas.OcupacaoPorHora(
            hora=hora,
            atendimentos=contagem_hora[hora],
            receita_total=round(receita_hora[hora], 2),
        )
        for hora in range(24)
    ]

    return schemas.RelatorioOcupacao(por_dia_semana=por_dia_semana, por_hora=por_hora)
