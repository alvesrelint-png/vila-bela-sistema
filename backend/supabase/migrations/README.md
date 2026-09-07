# Migrações

A estrutura das tabelas nasce aqui, em migração versionada (SQL ou via CLI do
Supabase), não em `Base.metadata.create_all()` do SQLAlchemy — ver convenção no
CLAUDE.md da raiz.

Sugestão de primeira migração (Sprint 1): criar `ingredientes`,
`lotes_estoque`, `movimentacoes`, `categorias`, `itens_cardapio` e
`fichas_tecnicas`, nessa ordem (respeitando as chaves estrangeiras).
`mesas`, `pedidos`, `itens_pedido` e `usuarios_internos` entram numa migração
do Sprint 2.
