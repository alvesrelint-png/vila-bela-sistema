# Arquitetura e Dados

## Estado da decisão técnica

> [!warning] Recomendação, não decisão fechada
> Abaixo está uma recomendação de stack com justificativa ligada a cada critério já definido pela equipe. Ela ainda depende de duas coisas que só o cliente e a equipe respondem: as restrições reais de dispositivo/internet (perguntas 9, 11 e 12 do roteiro em [[02 - Descoberta com o Cliente]]) e o conhecimento técnico de cada integrante (critério "Conhecimento da equipe" abaixo, hoje sem resposta). Trate isto como ponto de partida para a equipe ratificar ou trocar — não como stack definitiva.

## Diretrizes

- Aplicação web responsiva, acessível pelo navegador a partir do QR code.
- Área pública para consumidores e área protegida para operação.
- Fonte única de verdade para cardápio, estoque e pedidos.
- Atualizações críticas de estoque executadas de forma atômica.
- Histórico das movimentações relevantes, evitando alterações silenciosas de saldo.
- Interface simples para uso em celular, tablet ou computador.

## Modelo conceitual

| Entidade | Dados essenciais | Responsabilidade |
|---|---|---|
| Ingrediente | identificador, nome, unidade base, ativo | Representar o insumo controlado |
| Lote de estoque | ingrediente, quantidade atual, validade, data de entrada | Controlar saldo e vencimento por entrada |
| Movimentação | lote, tipo, quantidade, motivo, data | Registrar entrada, consumo, ajuste e reversão |
| Categoria | nome, ordem, ativa | Organizar o cardápio |
| Item do cardápio | categoria, nome, descrição, preço, ativo | Representar o produto vendido |
| Ficha técnica | item, ingrediente, quantidade necessária | Informar o consumo para preparar uma unidade |
| Mesa | código, identificação, ativa | Vincular QR code e pedido ao atendimento |
| Pedido | mesa, situação, datas, valor total | Controlar o ciclo do atendimento |
| Item do pedido | pedido, item, quantidade, preço registrado, observação | Preservar o que foi solicitado |
| Usuário interno | nome, acesso, situação | Proteger funções administrativas e operacionais |

## Regras de domínio

1. Cada ingrediente utiliza uma unidade base única no MVP: unidade, grama ou mililitro.
2. Lotes vencidos não compõem o saldo disponível.
3. Um item só está disponível quando está ativo e todos os ingredientes da ficha técnica possuem saldo válido suficiente.
4. A criação futura de um pedido deverá revalidar e reservar estoque em uma única operação.
5. O cancelamento restaura apenas a reserva associada ao pedido cancelado.
6. O preço e a descrição relevantes ao pedido devem ser preservados mesmo que o cardápio seja alterado depois.
7. Repetir uma solicitação após falha de conexão não pode criar o mesmo pedido duas vezes.

## Critérios para escolha da stack

| Critério | Pergunta |
|---|---|
| Conhecimento da equipe | Qual tecnologia o grupo consegue desenvolver e explicar na defesa? |
| Implantação | Existe opção simples e de baixo custo para publicar frontend, backend e dados? |
| Banco e transações | A solução suporta reserva de estoque e pedidos concorrentes com consistência? |
| Autenticação | É possível proteger a área da operação sem construir segurança do zero? |
| Responsividade | A interface funciona bem nos dispositivos reais da Vila Bela? |
| Manutenção | A equipe consegue corrigir e demonstrar a solução durante o semestre? |

## Registro de decisões

| Decisão | Estado | Justificativa |
|---|---|---|
| Aplicação web responsiva | Provisória | Compatível com acesso por QR code e múltiplos dispositivos |
| Pagamento fora do sistema | Aprovada para o MVP | Reduz escopo e riscos de integração |
| Estoque por lotes | Provisória | A validade pertence a cada entrada, não somente ao ingrediente |
| Reserva de estoque no pedido | Provisória | Evita aceitar pedidos concorrentes sem insumos |
| Stack tecnológica | Recomendada (ver abaixo) | Ligada aos critérios já definidos; pendente de ratificação pela equipe |

## Stack recomendada

> [!important] Publicação, não desenvolvimento do dia a dia
> Esta tabela descreve a stack para quando o projeto for **publicado de verdade**. Para desenvolver e demonstrar localmente, o esqueleto do repositório (`vila-bela-sistema/CLAUDE.md`) usa por padrão SQLite + senha única em vez de Supabase — assim ninguém da equipe precisa criar conta em nada só para rodar o projeto no próprio computador. A troca entre os dois é de poucas linhas (só a `DATABASE_URL`), então essa tabela continua sendo o destino final, não uma barreira de entrada.

| Camada | Recomendação | Por quê |
|---|---|---|
| Backend | Python com FastAPI | Curva de aprendizado curta para quem vem de lógica de programação básica, tipagem de dados explícita (ajuda a documentar a ficha técnica e o modelo de dados na defesa), e grande volume de tutoriais em português |
| Banco de dados | PostgreSQL | Suporta transação real: a reserva de estoque (regra 4 abaixo) pode ser feita com uma única instrução `UPDATE ... WHERE quantidade_disponivel >= necessária`, que falha sozinha se não houver saldo — resolve a "revalidação em uma operação única" já exigida pelas regras de domínio sem lógica extra de bloqueio |
| Hospedagem de banco + autenticação | Supabase (camada gratuita) | Entrega Postgres gerenciado e login pronto (e-mail/senha) na mesma plataforma — resolve o critério "Autenticação" sem a equipe construir isso do zero, e o critério "Implantação" com custo zero para um projeto acadêmico |
| Frontend | HTML, CSS e JavaScript simples (sem framework), responsivo | Sem etapa de build para os quatro integrantes gerenciarem, roda em qualquer navegador de celular ou tablet sem instalação — atende "Responsividade" e "Manutenção" mesmo se ninguém do grupo tiver experiência prévia com React ou similar |
| Hospedagem do frontend/backend | Vercel ou Render (camada gratuita) | Deploy direto a partir do repositório Git, sem servidor próprio para manter — resolve "Implantação" |

**Como isso atende cada critério já definido:**

- *Conhecimento da equipe:* stack com curva de entrada baixa e muito material em português; ainda assim, a equipe deve confirmar se algum integrante já tem experiência com outra stack que reduziria mais o risco — essa resposta continua em aberto.
- *Implantação:* Supabase + Vercel/Render cobrem banco, backend e frontend nas camadas gratuitas, sem cartão de crédito exigido para o uso básico.
- *Banco e transações:* PostgreSQL com `UPDATE` condicional resolve a reserva atômica de estoque (regra de domínio 4) sem exigir fila ou lock manual.
- *Autenticação:* Supabase Auth cobre o "Acesso administrativo" do MVP (Sprint 1) sem código de segurança escrito à mão.
- *Responsividade:* qualquer HTML/CSS responsivo atende; a validação real depende das perguntas 9, 11 e 12 do roteiro em [[02 - Descoberta com o Cliente]] sobre quais aparelhos a Vila Bela de fato usa.
- *Manutenção:* stack pequena, sem build step no frontend, e com abundância de tutoriais para os quatro integrantes se apoiarem durante o semestre.
