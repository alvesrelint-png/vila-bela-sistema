# Gestão Vila Bela

Sistema de cardápio digital, estoque e pedidos para o restaurante/bar Vila
Bela (Palmas). Projeto acadêmico (Projeto Integrador II).

## Antes de mexer no código, leia isto

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
│   │   ├── main.py          <- entrypoint FastAPI (registra os routers, cria as tabelas, seed de mesas)
│   │   ├── database.py      <- conexão com o banco (SQLite local / Postgres na publicação)
│   │   ├── models.py        <- 11 entidades (Sprint 1 + Sprint 2)
│   │   ├── schemas.py       <- schemas Pydantic
│   │   ├── routers/         <- uma rota por área: ingredientes, estoque, cardápio, mesas, pedidos, relatorios, auth
│   │   └── services/
│   │       ├── disponibilidade.py  <- cálculo central do Sprint 1 (item disponível/indisponível)
│   │       ├── estoque.py          <- reserva/baixa/reversão de estoque por pedido (Sprint 2)
│   │       └── relatorios.py       <- relatório de ocupação por dia da semana/hora
│   ├── supabase/migrations/ <- migrações versionadas do banco (só na publicação)
│   └── tests/
└── frontend/
    ├── tema.css              <- variáveis de cor/fonte
    ├── index.html            <- cardápio público (consumidor)
    ├── painel-estoque.html   <- ingredientes, lotes, cardápio e ficha técnica (Sprint 1)
    └── painel-pedidos.html   <- fila de pedidos, mesas e relatório de ocupação (Sprint 2)
```

Sprint 1 (estoque → cardápio) e Sprint 2 (mesa, pedido, pagamento registrado e
relatório de ocupação) estão implementados e testados. O que falta: o
carrinho self-service do consumidor (hoje é o operador quem lança o pedido,
pelo `painel-pedidos.html`) e o Sprint 3 (avisos de estoque baixo/validade,
histórico de pedidos e movimentações).

## Como rodar localmente

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
# cardápio público:      http://localhost:5500/index.html
# painel de estoque:      http://localhost:5500/painel-estoque.html
# painel de pedidos/mesas: http://localhost:5500/painel-pedidos.html
```

Nada disso pede Supabase — o banco é um arquivo SQLite criado automaticamente
na primeira execução (`backend/vila_bela.db`, já vem com 10 mesas cadastradas
de fábrica), e o login administrativo usa a senha do `.env`. Os dois painéis
administrativos compartilham o mesmo login (mesmo token salvo no navegador).
Supabase só entra na hora de publicar o projeto de verdade (ver `CLAUDE.md` >
Stack).

> Se você já tinha um `vila_bela.db` local de antes do Sprint 2, não precisa
> apagar nada — o `main.py` ajusta o esquema sozinho na primeira subida depois
> da atualização (ver `_migrar_esquema_sqlite()`).

## Antes de avançar para o carrinho self-service / Sprint 3

Os wireframes em `docs/planejamento/08 - Wireframes.md` ainda não foram
validados com o cliente (representante da Vila Bela) — e a conversa de
descoberta em `docs/planejamento/02 - Descoberta com o Cliente.md` também
segue pendente de conteúdo real. Vale resolver isso antes de trocar o
lançamento de pedido pelo operador por um carrinho self-service do
consumidor, para não implementar em cima de hipóteses erradas.
