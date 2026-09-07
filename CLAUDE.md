# Gestão Vila Bela — guia para quem for gerar o código

Este arquivo é o ponto de partida para o Claude Code (ou qualquer pessoa da equipe)
trabalhar neste repositório. Ele resume as decisões e regras já tomadas no
planejamento, que está inteiro em `docs/planejamento/` (era um vault do Obsidian —
os wikilinks `[[...]]` continuam funcionando como referência de leitura, mesmo fora
do Obsidian). Antes de gerar qualquer código, vale ler pelo menos:

- `docs/planejamento/01 - Visão do Produto.md` — problema, solução, escopo do MVP
- `docs/planejamento/04 - Backlog e MVP.md` — o que é Must/Should/Could e em qual sprint
- `docs/planejamento/05 - Arquitetura e Dados.md` — modelo de dados e regras de domínio
- `docs/planejamento/08 - Wireframes.md` — estrutura das telas

## O que é o projeto

Sistema para o restaurante/bar **Vila Bela** (Palmas) integrar três coisas que hoje
não conversam entre si: cardápio, estoque de ingredientes e pedidos. A regra
central: um item do cardápio só pode ser vendido se existir estoque válido
(não vencido) suficiente de **todos** os ingredientes da sua ficha técnica. Se
faltar qualquer um, o item fica indisponível automaticamente — sem intervenção
manual.

O consumidor acessa por QR code na mesa, escolhe pelo celular, sem instalar
aplicativo e sem criar conta. Pagamento é presencial, fora do sistema — o
sistema só **registra** valor e forma de pagamento por atendimento (mesa),
nunca processa pagamento de verdade (gateway/maquininha continuam fora do
MVP de propósito). O controle de mesas (pedidos, situação, tempo de
ocupação) e um relatório simples de ocupação por dia da semana/hora
entraram no MVP em 2026-09-07 — ver a nota em `01 - Visão do Produto.md`.

## Stack — dois ambientes diferentes, de propósito

Este projeto usa uma stack para **desenvolver localmente** (rápida, sem criar
conta em nada) e outra para **publicar de verdade** (a recomendação original de
`05 - Arquitetura e Dados.md`). Isso é intencional: a equipe não precisa de
Supabase só para conseguir rodar e demonstrar o projeto no dia a dia.

| Camada | Desenvolvimento local (padrão) | Publicação (quando for ao ar) |
|---|---|---|
| Backend | Python + FastAPI | Python + FastAPI (igual) |
| Banco | SQLite (arquivo único, zero instalação) | PostgreSQL via Supabase |
| Login administrativo | Senha única compartilhada, verificada no backend | Supabase Auth |
| Frontend | HTML + CSS + JS simples, sem build step | Igual |
| Hospedagem | A própria máquina de quem estiver desenvolvendo | Supabase (banco/auth) + Vercel ou Render |

A troca entre os dois é só a `DATABASE_URL` no `.env` (ver `.env.example`) —
o código em si (`app/database.py`, `app/models.py`) não muda entre os dois
ambientes, porque o SQLAlchemy abstrai isso. A única parte que exige atenção
na hora de migrar para Postgres é evitar SQL específico do SQLite nas queries
mais avançadas (a reserva de estoque com `UPDATE ... WHERE`, por exemplo,
funciona nos dois, mas vale testar em Postgres antes de publicar).

Se a equipe decidir por outra stack, atualize esta seção e `05 - Arquitetura e
Dados.md` juntos, para não ficarem contradizendo um ao outro.

## Ordem de implementação (por incremento — ver `04 - Backlog e MVP.md`)

**Sprint 1 — Estoque → Cardápio (o que este esqueleto já está preparado para receber):**
1. Cadastro de ingredientes
2. Registro de lotes (quantidade + validade)
3. Categorias e itens do cardápio
4. Ficha técnica (ingredientes necessários por item)
5. Cálculo de disponibilidade a partir do estoque válido
6. Cardápio público exibindo item disponível/indisponível
7. Acesso administrativo mínimo (protege cadastro de ingredientes/cardápio)

**Sprint 2 — Pedido integrado (implementado em 2026-09-07, depois do Sprint 1
pronto):** identificação da mesa, envio do pedido (lançado pelo operador —
carrinho self-service do consumidor fica para depois), fila operacional,
reserva e baixa de estoque, cancelamento com restauração, controle de mesas
(situação, tempo de ocupação), registro de pagamento por atendimento e
relatório de ocupação por dia da semana/hora — os três últimos ampliaram o
escopo original do MVP, ver `01 - Visão do Produto.md` e `04 - Backlog e
MVP.md`.

**Sprint 3 — Robustez:** avisos de estoque baixo/validade próxima, histórico de
movimentações.

Não adiante funcionalidade do Sprint 2/3 antes do Sprint 1 estar de pé — o
próprio backlog já foi corrigido para não misturar isso (ver o aviso no topo da
tabela MoSCoW em `04 - Backlog e MVP.md`).

## Modelo de dados (conceitual — `05 - Arquitetura e Dados.md`)

11 entidades: `Ingrediente`, `LoteEstoque`, `Movimentacao`, `Categoria`,
`ItemCardapio`, `FichaTecnica`, `Mesa`, `Atendimento`, `Pedido`, `ItemPedido`,
`UsuarioInterno`. `Atendimento` é a única que não estava no modelo original —
agrupa os pedidos de uma sentada da mesa (abre no 1º pedido, fecha quando a
conta é paga); `Pedido` referencia `Atendimento`, não `Mesa` diretamente. Os
nomes de campo estão no arquivo de arquitetura; `backend/app/models.py` já
implementa as 11 classes.

## Regras de domínio (não negociáveis sem atualizar o planejamento)

1. Cada ingrediente usa uma única unidade base no MVP: unidade, grama ou mililitro.
2. Lotes vencidos **não** entram no saldo disponível.
3. Um item só está disponível quando está ativo **e** todos os ingredientes da
   ficha técnica têm saldo válido suficiente.
4. A criação de um pedido deve revalidar e reservar estoque **em uma única
   operação** (evitar corrida entre pedidos concorrentes — no Postgres, um
   `UPDATE ... WHERE quantidade_disponivel >= necessária` resolve isso sem lock manual).
5. Cancelamento restaura só a reserva daquele pedido, nunca o saldo todo.
6. Preço e descrição do item pedido são congelados no momento do pedido — alterar
   o cardápio depois não pode reescrever pedidos já feitos (mesma lógica do
   `valor_cobrado` em outros projetos da casa: nunca recalcular histórico).
7. Reenviar uma requisição após falha de conexão não pode duplicar o pedido
   (idempotência).

## Convenções gerais

- **Nunca apagar de verdade.** Ingrediente, item de cardápio, mesa: usar um campo
  `ativo` e desativar, nunca `DELETE`. Isso preserva o histórico de pedidos e
  movimentações antigas.
- **Sem senha, token ou dado sensível em nenhum arquivo do repositório ou do
  vault** — regra já registrada em `07 - Evidências e Entregas.md`. Use
  variáveis de ambiente (`.env`, nunca commitado — ver `.gitignore`).
- Migrações de banco em `backend/supabase/migrations/`, versionadas — não usar
  `create_all` do SQLAlchemy em produção.
- Todo endpoint que mexe em estoque deve ser pensado para concorrência (dois
  pedidos ao mesmo tempo não podem ambos reservar o último ingrediente).

## O que já está implementado vs. o que falta

Sprint 1 (estoque → cardápio) e Sprint 2 (mesa, pedido, pagamento e relatório
de ocupação) estão implementados e testados — backend (`backend/app/`) e
frontend (`frontend/index.html`, `painel-estoque.html`, `painel-pedidos.html`).
Falta: o carrinho self-service do consumidor (hoje quem lança o pedido é o
operador, pelo `painel-pedidos.html`) e o Sprint 3 (avisos de estoque
baixo/validade, histórico de pedidos e movimentações). `backend/app/routers/`
e `backend/app/services/` seguem o mesmo padrão dos arquivos já prontos —
use-os como referência ao continuar.
