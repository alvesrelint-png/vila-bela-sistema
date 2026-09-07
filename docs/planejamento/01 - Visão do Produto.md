# Visão do Produto

## Situação

> [!warning] Hipótese a validar
> Esta visão foi construída a partir das anotações iniciais. Ela não deve ser apresentada como uma confirmação do cliente até que o registro da conversa seja incorporado em [[02 - Descoberta com o Cliente]].

## Cliente parceiro

- **Estabelecimento:** Vila Bela
- **Localidade informada:** Palmas
- **Representante:** `[PENDENTE: nome do representante da Vila Bela - irmão do Gabriel]`

## Hipótese do problema

A Vila Bela precisa reduzir a desconexão entre os ingredientes disponíveis, os itens apresentados no cardápio e os pedidos realizados pelos clientes. Sem essa integração, um item pode continuar aparecendo como disponível mesmo quando não existem ingredientes suficientes para prepará-lo.

## Hipótese da solução

Uma aplicação web responsiva acessada por QR code na mesa, composta por:

- cardápio digital para o consumidor;
- identificação da mesa e registro de pedidos;
- painel operacional de pedidos;
- cadastro e acompanhamento de ingredientes e lotes;
- ficha técnica relacionando cada item aos ingredientes necessários;
- disponibilidade automática dos itens conforme o estoque válido.

## Proposta de valor a validar

Oferecer ao cliente um cardápio atualizado e, à equipe da Vila Bela, uma visão integrada de estoque e pedidos, reduzindo pedidos de itens sem insumos disponíveis e melhorando a organização do atendimento.

## Usuários

| Usuário | Necessidade principal |
|---|---|
| Consumidor na mesa | Consultar itens disponíveis e enviar um pedido com poucos passos |
| Atendente ou caixa | Receber, acompanhar e concluir pedidos |
| Responsável pelo estoque | Registrar entradas, quantidades e validade dos ingredientes |
| Administrador | Manter cardápio, preços, fichas técnicas e acessos |

## Escopo inicial do MVP

- Cardápio público por QR code.
- Identificação da mesa.
- Itens organizados por categoria.
- Carrinho e envio do pedido.
- Fila operacional e situação do pedido.
- Cadastro de ingredientes e lotes.
- Fichas técnicas dos itens.
- Indisponibilidade automática baseada no estoque.
- Controle de mesas: pedidos lançados por mesa, situação (livre/ocupada) e
  há quanto tempo está ocupada.
- Registro de pagamento por atendimento (valor e forma — dinheiro/cartão/
  pix/outro) ao fechar a conta. Continua sendo só REGISTRO do que o
  operador informou, não processamento de pagamento (ver "Fora do MVP").
- Relatório simples de ocupação: quantos atendimentos e quanta receita por
  dia da semana e por horário — para saber quando a casa mais enche e
  quando mais fatura.

> [!note] Ampliação de escopo — 2026-09-07
> Os três itens acima (controle de mesas, registro de pagamento e
> relatório de ocupação) entraram no MVP a pedido da equipe, depois do
> Sprint 1 pronto. Antes disso, "pagamento integrado" e "relatórios
> avançados" estavam listados como fora do MVP — a distinção que
> permanece fora é o *processamento* de pagamento (gateway/maquininha) e
> relatórios *avançados* (indicadores, previsão de demanda), não o
> registro simples que entrou agora. Ver [[04 - Backlog e MVP]], seção
> "Segundo incremento", para os critérios de aceitação.

## Fora do MVP

- Pagamento processado pelo sistema (gateway, maquininha) — o pagamento
  continua acontecendo fora do sistema; o que entrou no MVP foi só o
  *registro* de valor/forma (ver acima).
- Delivery e cálculo de entrega.
- Emissão fiscal.
- Programa de fidelidade.
- Operação com várias filiais.
- Relatórios avançados, indicadores e previsão de demanda (dashboards,
  comparativos históricos, projeções) — o relatório simples de ocupação
  por dia/hora entrou no MVP (ver acima); análises mais sofisticadas
  continuam fora.

## Restrições pendentes

- [ ] Dispositivos utilizados pela equipe.
- [ ] Qualidade e disponibilidade da internet no estabelecimento.
- [ ] Quantidade aproximada de mesas, itens e pedidos por dia.
- [ ] Processo atual de pedidos e estoque.
- [ ] Pessoas autorizadas a manter cardápio e estoque.
- [ ] Necessidade de funcionar parcialmente sem internet.
- [ ] Regras de cancelamento e ajuste de estoque.
