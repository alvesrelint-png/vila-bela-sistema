# Jornada do Usuário e Fluxos da Solução

> [!warning] Rascunho para validação
> As jornadas abaixo representam a solução planejada e devem ser revisadas com a Vila Bela.

## Jornada do consumidor

| Etapa | Ação do usuário | Ponto de contato | Necessidade ou risco |
|---|---|---|---|
| Acesso | Escaneia o QR code da mesa | QR code e navegador | Abertura rápida, sem instalar aplicativo |
| Identificação | Confirma a mesa | Tela inicial | Evitar pedido enviado para mesa incorreta |
| Escolha | Navega por categorias e itens | Cardápio digital | Ver apenas itens realmente disponíveis |
| Montagem | Adiciona itens e observações | Carrinho | Entender preço, quantidade e composição |
| Confirmação | Revisa e envia o pedido | Resumo do pedido | Evitar envio duplicado ou incompleto |
| Acompanhamento | Consulta a situação | Tela do pedido | Saber se foi recebido e está em preparo |
| Pagamento | Paga presencialmente | Atendimento local | Pagamento permanece fora do sistema |

## Jornada da operação

| Etapa | Ação da equipe | Resultado esperado |
|---|---|---|
| Preparação | Registra ingredientes, lotes, quantidade e validade | Estoque inicial confiável |
| Configuração | Cadastra itens e respectivas fichas técnicas | Relação entre cardápio e insumos |
| Disponibilidade | Sistema calcula se os ingredientes são suficientes | Item disponível ou indisponível automaticamente |
| Recebimento | Operação recebe o pedido com mesa e itens | Pedido visível na fila |
| Produção | Atualiza a situação durante o preparo | Consumidor acompanha a evolução |
| Conclusão | Entrega e finaliza o pedido | Pedido encerrado e estoque consistente |
| Cancelamento | Cancela com motivo quando necessário | Reserva ou baixa de estoque revertida |

## Fluxo estrutural do primeiro incremento

1. Operador cadastra um ingrediente e define sua unidade base.
2. Operador registra um lote com quantidade e validade.
3. Operador cadastra um item do cardápio.
4. Operador cria a ficha técnica com os ingredientes necessários por unidade do item.
5. O sistema soma somente o estoque válido e compara com a ficha técnica.
6. O cardápio exibe o item como disponível ou indisponível.

## Fluxo futuro do pedido

1. Consumidor abre o cardápio pelo QR code da mesa.
2. Sistema apresenta itens e disponibilidade atual.
3. Consumidor monta e confirma o pedido.
4. Sistema valida e reserva os ingredientes em uma operação única.
5. Operação recebe o pedido e atualiza sua situação.
6. Cancelamento restaura a reserva; conclusão consolida a baixa.

## Situações de exceção

- Estoque vencido não torna um item disponível.
- Quantidade insuficiente de qualquer ingrediente bloqueia o item.
- Pedido concorrente deve revalidar o estoque antes da confirmação.
- Cancelamento deve restaurar apenas a quantidade efetivamente reservada.
- Item desativado manualmente permanece indisponível mesmo com estoque.
- Falha de conexão não pode criar pedidos duplicados.
