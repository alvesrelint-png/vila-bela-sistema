# Gestão Vila Bela

Sistema de cardápio digital, estoque e pedidos para o restaurante/bar Vila
Bela (Palmas). Projeto acadêmico (Projeto Integrador II).

## Antes de codar, leia isto

- **`CLAUDE.md`** — resumo das regras de negócio, stack e ordem de
  implementação. Se você for usar o Claude Code neste repositório, ele já lê
  esse arquivo automaticamente.
- **`docs/planejamento/`** — todo o planejamento original (vault do Obsidian):
  visão de produto, descoberta com o cliente, jornada, backlog/MoSCoW,
  arquitetura e modelo de dados, sprints, wireframes. É a fonte de verdade por
  trás de tudo que está no CLAUDE.md.

## Estrutura

```
vila-bela-sistema/
├── CLAUDE.md
├── docs/planejamento/       <- toda a documentação de planejamento
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── app/
│   │   ├── main.py          <- entrypoint FastAPI
│   │   ├── database.py      <- conexão com o Postgres/Supabase
│   │   ├── models.py        <- 10 entidades (stub, ver TODOs)
│   │   ├── schemas.py       <- schemas Pydantic (stub)
│   │   ├── routers/         <- uma rota por área (ingredientes, estoque, cardápio, pedidos, auth)
│   │   └── services/
│   │       └── disponibilidade.py  <- cálculo central do projeto
│   ├── supabase/migrations/ <- migrações versionadas do banco
│   └── tests/
└── frontend/
    ├── tema.css              <- variáveis de cor/fonte
    ├── index.html            <- cardápio público
    ├── painel-estoque.html   <- área administrativa (Sprint 1)
    └── painel-pedidos.html   <- fila operacional (Sprint 2)
```

Todo arquivo de código aqui é **esqueleto**: contém só estrutura e comentários
`# TODO` explicando o que precisa ser implementado e em qual sprint — nenhuma
lógica de verdade foi escrita ainda, de propósito.

## Como começar

1. Abra este repositório no Claude Code (ou no editor de sua preferência).
2. Peça para implementar o Sprint 1, seguindo a ordem que está no `CLAUDE.md`
   — comece por `app/models.py`, depois `database.py`, os routers de
   ingredientes/estoque/cardápio, e o service de disponibilidade.
3. Copie `.env.example` para `.env` (dentro de `backend/`). O padrão já vem
   configurado para SQLite — **não precisa criar conta em nada** para rodar
   localmente; só troque `ADMIN_SENHA` por uma senha sua.
4. Depois que o backend do Sprint 1 estiver de pé, conecte o
   `frontend/index.html` e o `frontend/painel-estoque.html` a ele.

## Como rodar localmente (depois que o código estiver implementado)

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # ajuste ADMIN_SENHA
uvicorn app.main:app --reload  # sobe em http://localhost:8000
```

Em outro terminal, com o backend ainda rodando:

```bash
# Frontend
cd frontend
python3 -m http.server 5500
# abra http://localhost:5500/index.html no navegador
```

Nada disso pede Supabase — o banco é um arquivo SQLite criado automaticamente
na primeira execução (`backend/vila_bela.db`), e o login administrativo usa a
senha do `.env`. Supabase só entra na hora de publicar o projeto de verdade
(ver `CLAUDE.md` > Stack).

## Antes de avançar para o Sprint 2

Os wireframes em `docs/planejamento/08 - Wireframes.md` ainda não foram
validados com o cliente (representante da Vila Bela) — e a conversa de
descoberta em `docs/planejamento/02 - Descoberta com o Cliente.md` também
segue pendente de conteúdo real. Vale resolver isso antes de construir o
fluxo de pedido do Sprint 2, para não implementar em cima de hipóteses erradas.
