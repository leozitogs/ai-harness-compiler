# Sprint 2.6 — resultado técnico da compatibilidade após UTF-8

Data: 2026-10-27. Rodada concluída; orçamento fechado; revisão semântica pendente.

O PO autorizou uma única rodada do request
`4d4a7f98cf43d5f7fb39f4c31bb64ca07e47a8aa26aca4132f877c335401d2a7`,
respondendo “Autorizo esta única rodada nesses limites”. O runner usou o caso
e o código congelados do PR #78. Não houve retry, repair, fallback ou retomada.

| Evidência observada | Resultado |
| --- | --- |
| Rodada | `compat-v4-catalog-20261027-03` |
| Caso | `compat-catalog-v4-01`, expectativas aprovadas preservadas |
| Destino/modelo solicitado | Assinatura ChatGPT/Codex CLI; `gpt-6.1-sol` |
| Invocações debitadas | Duas: análise v4, depois auditoria v5 |
| Transporte e contratos | Ambas as etapas aceitas; fluxo e relatório externo `completed` |
| Tempos observados | Análise 21,2373s; auditoria 36,9244s; sessão 58,9332s |
| Contenção e encerramento | Windows Job Object em ambas; raízes encerradas e coletadas |
| Integridade | Replay offline verificado; hashes e vínculos preservados |
| Assessment inicial | `not-run`; seis julgamentos humanos pendentes |
| Orçamento | Fechado; nenhuma nova invocação autorizada por este resultado |

As etapas couberam nos limites específicos: 180s por chamada, reserva de limpeza
de até 20s dentro de sessão de 400s e 1 MiB/4 MiB de entrada/saída por worker.
Os [metadados públicos](../evidence/sprint-2-6-v4-utf8-compatibility-20261027/execution.json)
registram recibos, hashes dos artefatos privados, request e limites. Não publicamos
prompts, respostas integrais ou journals; permanecem privados em `.factory/`.

## O que a execução estabelece

Observamos compatibilidade dos schemas de análise v4 e auditoria v5 neste request:
ambas as respostas foram aceitas pelos contratos e pelos validadores de vínculos.
A fronteira UTF-8 transmitiu esta resposta sem o erro anterior. O resultado não
prova a causa única dos bytes descartados da rodada anterior nem compatibilidade
de todos os schemas, casos, versões ou futuros deployments do provedor.

A identidade remota do modelo não é autenticada; registramos o modelo solicitado.
As durações são observações de uma única rodada via serviço remoto, sem alegar
medianas, repetibilidade de performance, cold/warm ou consumo de VRAM local.

## Próximo gate: revisão humana da análise

A análise resultante tem snapshot:
`ee19775d4007c74f56a1af26c92b945d9bd8a7970d51a30a374761f5d32f1ad8`.

O assessment inicial não encontrou os impedimentos determinísticos que verifica,
mas continua `not-run` em todos os seis critérios humanos. Isso não é passe
semântico. O parecer do auditor também não substitui aprovação humana.

Preparamos o documento privado
`.factory/v4-utf8-compatibility-po-review/po-review.md`, com fontes exatas, resposta
integral da análise, acesso à auditoria, quatro mapeamentos de cobertura e os
dez achados/quinze componentes com seus textos, fontes e hashes. A proposta contém
recomendações de engenharia, sem declarar aceite em nome do PO.

Hash da proposta de revisão ainda pendente:
`d5bed82926844418306e81bded8a39ff548b10182848bba0b49450a58645e3d0`.

O aceite futuro deverá distinguir a condição necessária de aprovação de uma
autorização suficiente para publicar, preservar identidade/origem sem gatilhos
inventados e julgar a rejeição apenas do fragmento malicioso. Inclui revisar o
significado do campo de custo de build normalizado, sem equipará-lo ao orçamento
específico de inferência. Não houve leitura de assets ou do reservado.

| Trabalho | Dependência | Verificação |
| --- | --- | --- |
| Registrar execução | Request e autorização exatos | Duas etapas, limites, hashes, replay e orçamento fechado |
| Preparar revisão | Artefatos aceitos | Fontes e proposta vinculadas ao snapshot, sem aprovação automática |
| Julgar saída | Revisão explícita do PO | Seis critérios e todos os vínculos necessários; falhas preservadas |
| Consolidar desenvolvimento | Julgamento registrado | Corpus compatível e orçamento próprios para comparação ampliada |
| Qualificar ou rejeitar | Candidato congelado e avaliação independente | Qualidade e recursos observados; não extrapolar este caso |

Nenhuma história foi marcada Done. O resultado não qualifica o modelo, promove
defaults, autoriza compilação ou encerra a Sprint 2.6. A
[sequência de entregas](sprint-2-6-next-sequence.md) permanece sujeita aos seus gates.
