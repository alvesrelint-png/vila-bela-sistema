# Backlog e MVP

## Priorização MoSCoW

> [!important] Revisão: recorte por incremento
> A versão anterior desta tabela marcava 11 itens como "Must" ao mesmo tempo, incluindo cardápio, estoque **e** pedido — mas [[06 - Sprints e Responsabilidades]] já planeja o pedido só para o Sprint 2, depois do incremento Estoque → Cardápio do Sprint 1. Ou seja, o MoSCoW e o plano de sprints se contradiziam sobre o que é "essencial primeiro". A coluna **Incremento-alvo** abaixo resolve isso: um item continua Must para o MVP completo, mas fica claro em qual sprint ele precisa existir — isso é o que de fato orienta o que entra no Sprint 1.

| Funcionalidade | Classificação | Incremento-alvo | Pertence ao MVP completo? | Justificativa |
|---|---|---|---:|---|
| Cadastro de ingredientes | Must | Sprint 1 | Sim | Base do controle de estoque; sem isso nada mais no incremento funciona |
| Registro de lotes, quantidade e validade | Must | Sprint 1 | Sim | Permite controlar saldo utilizável e vencimento |
| Categorias e itens com preço e descrição | Must | Sprint 1 | Sim | Estrutura mínima de um cardápio utilizável |
| Ficha técnica do item | Must | Sprint 1 | Sim | Define o consumo necessário de cada ingrediente |
| Indicação automática de item indisponível | Must | Sprint 1 | Sim | Resolve a integração central entre estoque e cardápio — é a hipótese central do projeto |
| Cardápio público acessado por QR code | Must | Sprint 1 (exibição) / Sprint 2 (fluxo completo) | Sim | O Sprint 1 já precisa exibir o cardápio com disponibilidade; o QR/identificação de mesa entra no Sprint 2 |
| Acesso administrativo (mínimo) | Must | Sprint 1 | Sim | Protege cadastro de ingredientes e cardápio; pode começar simples (uma senha da equipe) e evoluir depois |
| Identificação da mesa | Must | Sprint 2 | Sim | Só faz sentido junto do fluxo de pedido, que ainda não existe no Sprint 1 |
| Carrinho e envio do pedido | Must | Sprint 2 | Sim | Completa a jornada principal do consumidor |
| Fila e situação dos pedidos | Must | Sprint 2 | Sim | Permite à operação receber e conduzir o atendimento |
| Reserva e baixa segura de ingredientes | Must | Sprint 2 | Sim | Só é necessária quando pedidos concorrentes existem — não há pedido no Sprint 1 |
| Cancelamento com restauração de estoque | Should | Sprint 2 | Sim | Evita divergência após cancelamentos; depende do pedido existir |
| Aviso de estoque baixo | Should | Sprint 3 | Sim | Ajuda a prevenir indisponibilidade inesperada |
| Aviso de validade próxima | Should | Sprint 3 | Sim | Apoia redução de perdas |
| Histórico de pedidos e movimentações | Should | Sprint 3 | Sim | Facilita conferência e rastreabilidade |
| Geração e impressão do QR das mesas | Could | Sprint 2 | Não | Pode ser feita inicialmente por ferramenta externa (gerador de QR gratuito) |
| Personalização visual avançada | Could | — | Não | Não é essencial para provar os fluxos |
| Relatórios e indicadores avançados | Could | — | Não | Dependem de dados acumulados ao longo do uso |
| Pagamento integrado | Won't | — | Não | Aumenta risco e complexidade sem ser necessário no MVP |
| Delivery | Won't | — | Não | Está fora do atendimento por QR code na mesa |
| Emissão fiscal | Won't | — | Não | Exige integrações e regras externas ao objetivo acadêmico |

## Primeiro incremento - Estoque → cardápio

### Objetivo

Demonstrar que a disponibilidade do cardápio responde automaticamente à quantidade e à validade dos ingredientes registrados.

### Histórias de usuário

- Como responsável pelo estoque, quero cadastrar ingredientes e lotes para conhecer o saldo válido disponível.
- Como administrador, quero definir os ingredientes de cada item para que o sistema calcule sua disponibilidade.
- Como consumidor, quero identificar itens indisponíveis para não tentar pedir algo que não pode ser preparado.

### Critérios de aceitação

- [ ] Cadastrar ingrediente com nome e unidade base.
- [ ] Registrar lote com quantidade positiva e data de validade.
- [ ] Cadastrar item do cardápio com nome, categoria, preço e situação ativa.
- [ ] Relacionar um ou mais ingredientes ao item com quantidade necessária.
- [ ] Considerar apenas lotes não vencidos no cálculo.
- [ ] Marcar o item como indisponível quando faltar qualquer ingrediente.
- [ ] Recalcular a disponibilidade após entrada, ajuste ou vencimento de estoque.
- [ ] Impedir seleção do item indisponível no cardápio público.

## Backlog da Sprint 0

- [ ] Incorporar o registro da conversa com o cliente.
- [ ] Confirmar problema, usuários e proposta de valor.
- [ ] Confirmar dispositivos, internet e volume da operação.
- [ ] Validar jornada e fluxos.
- [ ] Definir responsáveis da equipe.
- [ ] Revisar e aprovar o MVP.
- [ ] Escolher a stack com base nas restrições levantadas.
