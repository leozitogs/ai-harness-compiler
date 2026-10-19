# AHC-029 — Operador autorizado e recuperação

2026-10-19. Continuação explicitamente autorizada pelo PO após integração da AHC-028.
O incremento implementa plano de operação, autorização por hash exato, recibos e
journal SQLite, com adapter GitHub limitado a adicionar etiquetas de pendência.
AHC-027/028/029 continuam em revisão; não há aceite por critério ou sprint concluída.

## Resultado observado

[Inventário de evidências](../evidence/ahc-029-operator-20261019/inventory.json).
Na simulação offline, uma autorização **fictícia de teste**, explicitamente rotulada,
levou a uma tentativa e um efeito no adapter fake. Timeout após a escrita deixou
uncertain. Reconciliação somente leitura observou o resultado; replay devolveu o
mesmo recibo, sem nova escrita. Cinco recibos encadeados foram reabertos e validados
no journal. 2 leituras fake: preflight e reconciliação. A consulta posterior ao POST
não ocorre no cenário de timeout; o replay não faz rede.

O fixture mantém `declared_goal_outcome=not-achieved` e aceite não estabelecido.
O review real da Sprint 2.5 continua na captura da AHC-028; este fixture isolado
não atualiza seu horário nem apresenta dados sintéticos como observações reais.
Houve um smoke fake preliminar antes da captura final, sem efeito externo.

O adapter real fez somente um GET na issue #46: confirmou projeção de metadados e
hashes, host e versão da API. **Nenhum POST real foi executado.** A criação de PR e
atualização administrativa da história pelo colaborador são ações separadas da demo
do operador. Não são evidência de integração real da escrita implementada.

## Verificação e limites

50 novos testes offline cobrem replay, crash antes/depois da escrita e antes do
recibo, timeout, concorrência, alvo reservado, cancelamento, autorização vencida,
fontes alteradas, allowlist, diff divergente, recibos imutáveis e banco adulterado.
O adapter tem testes de host fixo, endpoint aditivo, payload, guard final, timeout,
limite de stdout e metadados malformados. Nenhuma chamada de modelo na demonstração.

O journal coordena workers que compartilham o mesmo arquivo; outros hosts/journals
não compartilham a reserva. Estado remoto pode mudar entre leitura e escrita: não
há CAS ou exactly-once remoto. Alterações concorrentes não são substituídas pela
operação aditiva; divergências observadas ficam no recibo e mantêm uncertain.
Efeito não estabelecido permanece bloqueado, sem liberação administrativa automática.

Cancelamento só existe antes do dispatch. Actor é declaração do operador confiável,
não identidade autenticada. Uma escrita real exige aprovação humana específica do
diff, observação atual e etiqueta existente. Estados, marcos e ordenação do backlog
continuam fora da allowlist. Ver [ADR-0025](../adr/0025-authorized-scrum-operation-journal.md).


## Checks finais

907 testes passaram, sem skips, com todos os extras (50 novos nesta etapa).
Ruff, formatação, mypy, schemas, instruções geradas e quatro planos passaram.
Build, integridade da memória e CI do PR completam o gate de integração; não
representam aceite humano ou validação real do POST.
