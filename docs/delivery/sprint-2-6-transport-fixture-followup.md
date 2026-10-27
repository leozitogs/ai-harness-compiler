# Sprint 2.6 — prazo da fixture de integridade do transporte

Data: 2026-10-27. Alteração restrita a testes; pedido final e runtime preservados.

Na preparação do pedido revisado, a primeira execução focada terminou com 85
testes aprovados e um reprovado. A fixture `prepare` do teste de integração usava
sessão de 15 segundos para todo o fluxo, incluindo conferência de fontes,
validação tipada e persistência. O relatório registrou 16,6926969 segundos de
sessão, embora as duas etapas internas estivessem concluídas e ambos os recibos
fossem bem-sucedidos. Os workers consumiram aproximadamente 0,219 segundo somados.

O runtime classificou corretamente a sessão externa como `failed`: ultrapassar
o limite não pode produzir sucesso apenas porque os workers terminaram. A
asserção do teste esperava `completed`, tornando esse caminho de integridade
também uma exigência implícita de desempenho do host. As medições não identificam
qual operação fora dos workers consumiu cada parcela do tempo; não demonstram
que o provedor ou o sistema de produção falhou.

O helper de integração passa a usar sessão de 120 segundos somente para testes
sintéticos. O teto por worker continua três segundos; a reserva de limpeza
continua dois. Os testes específicos de timeout, ausência de saldo, contenção e
interrupção permanecem. O teste de relatório excedido usa agora
`request.limits.session_timeout_seconds + 1`, preservando a reprovação em função
do limite da própria fixture, sem constante absoluta que possa ficar abaixo dele.

Nenhum default, contrato, fonte de produção, prompt ou schema mudou. O pedido
final continua congelado no hash
`2e8963f18cb88f2dc7d70e737a0bafe8872b822a149c6f1985c66e48ae2f60cd`,
com sessão proposta de 400 segundos e execução não autorizada. Aumentar o teto
da fixture de integridade não mede nem certifica desempenho; os prazos de uma
rodada real continuam sujeitos ao runner e ao orçamento específico do PO.

| Etapa | Dependência | Verificação |
| --- | --- | --- |
| Diagnóstico | Relatório original | Preservar falha externa e os dois recibos bem-sucedidos |
| Correção da fixture | Diagnóstico | Integridade não exige implicitamente desempenho em 15s |
| Controle de excesso | Limite explícito | Resultado acima do teto não aceita `completed` |
| Regressão | Correção | Suíte focada offline e matriz CI antes de integrar |

O [registro inicial](../evidence/sprint-2-6-v4-reviewed-20261027/initial-local-failure.json)
contém apenas metadados de uma execução sintética local; não é avaliação de modelo.
