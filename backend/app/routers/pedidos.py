"""
Rotas de mesa e pedido — SPRINT 2. Não implementar antes do Sprint 1 (estoque
-> cardápio) estar funcionando de ponta a ponta; ver a ordem de implementação
no CLAUDE.md da raiz do repositório.

# TODO (quando chegar a hora):
# - POST /mesas/{codigo}/pedidos     criar pedido: revalidar e reservar estoque
#     em uma única operação (regra de domínio 4) — no Postgres, considerar um
#     UPDATE condicional (`WHERE saldo >= necessário`) por ingrediente da ficha
#     técnica, dentro de uma transação, revertendo tudo se qualquer um falhar.
# - PATCH /pedidos/{id}/situacao     avançar fila (recebido -> preparo -> pronto -> entregue)
# - PATCH /pedidos/{id}/cancelar     restaura só a reserva deste pedido (regra 5)
# - GET  /pedidos                    fila operacional (painel — ver wireframe 5)
# - GET  /mesas/{codigo}/pedidos/{id}  acompanhamento do cliente (wireframe 4)
"""
