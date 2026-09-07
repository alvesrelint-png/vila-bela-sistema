# Wireframes de Baixa Fidelidade

> [!important] O que isto é e o que não é
> O enunciado da disciplina (ver [[99 - Rascunhos Originais]]) pede wireframes como etapa de **estrutura lógica**, não de estética: "esta etapa não trata de estética, mas da estrutura lógica da solução". Por isso os esboços abaixo são propositalmente crus — texto e caixas, sem cor, fonte ou logotipo. Isto substitui a ausência total de wireframes ou protótipo que existia no vault, mas **não substitui** o protótipo navegável de alta fidelidade em Figma que o enunciado também exige — este é o passo seguinte, depois de validar a hierarquia abaixo com o cliente.

> [!warning] Rascunho a validar
> Estas telas foram derivadas da jornada já registrada em [[03 - Jornada e Fluxos]] e do escopo do MVP em [[01 - Visão do Produto]] e [[04 - Backlog e MVP]]. Nenhuma foi vista pelo cliente ainda — é o próximo item da lista de ratificação em [[00 - Projeto]].

## Mapa de telas

```text
[Consumidor]                          [Operação / Admin]

QR da mesa                            Login da operação
   |                                      |
Cardápio (lista)  ---> Detalhe do item    Painel de estoque
   |                        |                 |
   v                        v                 +-- Ingredientes
Carrinho  <------------------                 +-- Lotes
   |                                          +-- Itens do cardápio
   v                                          +-- Fichas técnicas
Confirmação do pedido                         |
   |                                          v
   v                                     Fila de pedidos (Sprint 2)
Acompanhamento do pedido (Sprint 2)
```

## 1. Cardápio público (mobile) — Sprint 1

Tela que o consumidor vê ao ler o QR code da mesa. É a tela que prova a hipótese central: item sem estoque aparece visivelmente bloqueado.

```text
┌─────────────────────────────┐
│  VILA BELA                  │  <- nome do estabelecimento
│  Mesa 07                    │  <- identificação (Sprint 2; no Sprint 1 pode ficar fixo/oculto)
├─────────────────────────────┤
│ [Entradas] [Pratos] [Bebidas]│  <- categorias, rolagem horizontal
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │ Bruschetta               │ │
│ │ R$ 24,90                 │ │
│ │ [ DISPONÍVEL ]           │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ Tábua de frios           │ │
│ │ R$ 39,90                 │ │
│ │ [ INDISPONÍVEL ]         │ │  <- item cinza/opaco, sem botão de adicionar
│ │ sem estoque no momento   │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ Pão de alho               │ │
│ │ R$ 18,00                 │ │
│ │ [ DISPONÍVEL ]           │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
```

**Decisões de estrutura:** categorias em abas horizontais (não menu lateral) para caber em tela pequena; o rótulo de disponibilidade fica dentro do próprio cartão do item, não como ícone isolado, porque é a informação mais importante da tela — precisa ser lida sem interpretação.

## 2. Detalhe do item e carrinho — Sprint 2

```text
┌─────────────────────────────┐
│ < Voltar      Bruschetta    │
├─────────────────────────────┤
│ Descrição do prato...        │
│ R$ 24,90                     │
│                               │
│ Observação (opcional)         │
│ [________________________]   │
│                               │
│ Quantidade   [ - ]  1  [ + ]  │
│                               │
│ [   Adicionar ao carrinho  ]  │
├─────────────────────────────┤
│ Carrinho (2 itens) — R$ 43,80│  <- barra fixa inferior, some se vazio
└─────────────────────────────┘
```

## 3. Confirmação do pedido — Sprint 2

```text
┌─────────────────────────────┐
│  Confirmar pedido — Mesa 07  │
├─────────────────────────────┤
│ 1x Bruschetta        R$24,90 │
│ 1x Pão de alho        R$18,00│
│                               │
│ Total              R$ 42,90  │
│                               │
│ [   Enviar pedido para a    ] │
│ [   cozinha                 ] │
├─────────────────────────────┤
│ Pagamento é feito no balcão, │  <- lembrete: pagamento fora do sistema
│ ao final do atendimento.      │
└─────────────────────────────┘
```

## 4. Acompanhamento do pedido — Sprint 2

```text
┌─────────────────────────────┐
│  Seu pedido — Mesa 07        │
├─────────────────────────────┤
│  ( ) Recebido                │
│  (•) Em preparo               │  <- situação atual destacada
│  ( ) Pronto                  │
│  ( ) Entregue                 │
├─────────────────────────────┤
│ 1x Bruschetta                │
│ 1x Pão de alho                │
└─────────────────────────────┘
```

## 5. Painel operacional — fila de pedidos (tablet/desktop) — Sprint 2

```text
┌───────────────────────────────────────────────────────────┐
│ VILA BELA — Painel de pedidos            [Sair]            │
├───────────────┬───────────────┬───────────────┬───────────┤
│ Recebidos      │ Em preparo     │ Prontos        │ Entregues │
├───────────────┼───────────────┼───────────────┼───────────┤
│ Mesa 07        │ Mesa 03        │ Mesa 12        │ Mesa 05   │
│ 2 itens        │ 1 item         │ 3 itens        │ 4 itens   │
│ [Iniciar >]    │ [Pronto >]     │ [Entregar >]   │           │
│                │               │               │           │
│ Mesa 09        │               │               │           │
│ 1 item         │               │               │           │
│ [Iniciar >]    │               │               │           │
└───────────────┴───────────────┴───────────────┴───────────┘
```

**Decisão de estrutura:** colunas por situação (estilo Kanban) em vez de lista única — é a forma mais direta de mostrar o fluxo definido em [[03 - Jornada e Fluxos]] sem precisar de filtros.

## 6. Painel de estoque — cadastro de ingredientes e lotes (desktop) — Sprint 1

Esta é a tela que sustenta o incremento do Sprint 1 — sem ela, ninguém alimenta o cálculo de disponibilidade.

```text
┌───────────────────────────────────────────────────────────┐
│ VILA BELA — Estoque    [Ingredientes] [Lotes] [Fichas]      │
├───────────────────────────────────────────────────────────┤
│ Ingredientes                              [+ Novo ingrediente]│
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Nome          │ Unidade │ Saldo válido │ Situação     │   │
│ │ Queijo brie   │ g       │ 480 g        │ Ativo        │   │
│ │ Pão italiano  │ un      │ 6 un         │ Ativo        │   │
│ │ Presunto parma│ g       │ 0 g          │ Ativo        │   │
│ └─────────────────────────────────────────────────────┘   │
│                                                             │
│ [Presunto parma selecionado]                               │
│ Lotes deste ingrediente                    [+ Novo lote]    │
│ ┌─────────────────────────────────────────────────────┐   │
│ │ Quantidade │ Validade    │ Entrada     │ Situação     │   │
│ │ 200 g      │ 03/09/2026  │ 20/08/2026  │ Vencido      │   │
│ └─────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

**Decisão de estrutura:** lotes aparecem "dentro" do ingrediente selecionado (mestre-detalhe), não numa lista solta — porque a regra de domínio 2 em [[05 - Arquitetura e Dados]] diz que a validade pertence ao lote, não ao ingrediente, e a tela precisa deixar isso visível: dá para ver o mesmo ingrediente com um lote vencido e outro válido ao mesmo tempo.

## Ficha técnica (vinculada ao item do cardápio) — Sprint 1

```text
┌───────────────────────────────────────────────────────────┐
│ Ficha técnica — Tábua de frios                              │
├───────────────────────────────────────────────────────────┤
│ Ingrediente        │ Quantidade necessária                  │
│ Presunto parma     │ 80 g                                    │
│ Queijo brie        │ 60 g                                    │
│ Pão italiano       │ 2 un                                    │
│                                                             │
│ [+ Adicionar ingrediente à ficha]                            │
│                                                             │
│ Disponibilidade calculada: INDISPONÍVEL                      │
│ (falta: presunto parma — saldo válido 0 g, necessário 80 g)  │
└───────────────────────────────────────────────────────────┘
```

**Decisão de estrutura:** a tela mostra o motivo do bloqueio (qual ingrediente falta), não só o resultado — isso vem direto do critério de aceitação "marcar o item como indisponível quando faltar qualquer ingrediente" em [[04 - Backlog e MVP]], e evita que a equipe precise investigar no banco por que um item sumiu do cardápio.

## Próximo passo

- [ ] Validar esta hierarquia com o representante da Vila Bela (pergunta aberta no roteiro de [[02 - Descoberta com o Cliente]]).
- [ ] Depois de validado, montar o protótipo navegável de alta fidelidade em Figma exigido pelo enunciado ([[99 - Rascunhos Originais]]), usando estas telas como base de navegação.
