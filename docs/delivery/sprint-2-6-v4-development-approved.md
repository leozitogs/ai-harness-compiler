# Sprint 2.6 — expectativas v4 aprovadas e preparação da campanha

Data: 2026-10-27. Expectativas congeladas; campanha ainda não autorizada.

O PO declarou **“Li e aprovo as expectativas dos oito casos”**, em resposta a
`call_1a520665d7ed48b58e348c28046906b2`, vinculada ao manifesto proposto
`952e1dd71495e950eb3d9ba625db82d31538eb6a5c5ac9bf10dadd03c6897a9b`.
O aceite abrange as expectativas descritas na
[tabela revisada](sprint-2-6-v4-human-review-development.md), incluindo os limites
específicos de regras A/B, identidade, conflito, ambiguidade, assets e injeção.

Foram criados oito novos snapshots `AssessmentCase/v3`. A única mudança em cada
caso é `expectations_approval`, com a declaração humana recebida. Inputs,
obrigações, citações, disposição esperada e rejeições permanecem idênticos às
propostas. Estas continuam intactas e pendentes no seu registro histórico.

O [manifesto revisado](../../evals/understanding/v4/development-reviewed/manifest.json)
tem digest canônico:

`8f666df68dcc150caaa085051487784ec907219d8ab7f78de8b120f480f7381b`.

Ele vincula o manifesto proposto, arquivos originais, casos novos, projetos,
rubrica inalterada e a pergunta/resposta do PO. Os oito preflights foram refeitos
com os novos hashes e são compatíveis. A declaração é humana recebida no chat,
sem autenticação criptográfica. Os testes conferem a preservação dos dados e
impedem que o registro do aceite seja apresentado como autorização de execução.

São seis casos esperados `ready` e dois `blocked`. Esses são resultados esperados,
não resultados observados do candidato. Nenhuma nova resposta foi produzida ou
julgada. O conjunto é desenvolvimento exposto, sem independência estatística ou
direito de ser reutilizado como holdout cego.

## Plano do próximo incremento: controle global

O runtime existente supervisiona um caso com duas etapas. Antes de executar oito
casos, implementar um controlador que compartilhe prazo, contagem e encerramento
entre todos eles. Um loop de oito sessões independentes não cumpre esse requisito.
Este documento é um plano de implementação, não um pedido executável ou uma
autorização. Não há novo hash de pedido para aprovar nesta etapa.

| Tarefa | Dependência | Entrega e verificação |
| --- | --- | --- |
| C1 — contrato da campanha | Corpus revisado acima | Pedido tipado com ordem dos oito casos, rubrica, programas, modelo solicitado, limites e fontes congeladas; rejeitar duplicatas, casos sem aceite, hashes divergentes e limites inconsistentes. Exportar schemas. |
| C2 — controlador global | C1 | Um relógio monotônico e um teto global; debitar cada invocação antes de iniciar o worker; preservar limpeza e reaping existentes. Nenhum worker após encerramento ou esgotamento. |
| C3 — persistência e replay | C2 | Claim exclusivo do pedido, journals e recibos vinculados a caso/etapa; verificar ordens, limites e fontes. Pedido consumido não pode ser retomado ou reutilizado, inclusive após falha. |
| C4 — testes offline adversariais | C1–C3 | Workers locais e relógio controlado: prazo entre casos, estouro de saída, hash alterado, caso repetido, segundo lançamento indevido, falha na auditoria, cancelamento e limpeza de descendentes. Sem chamadas de modelo. |
| C5 — congelar pedido concreto | C4 e CI/revisão | Preservar replay da compatibilidade anterior antes de alterar fontes; congelar nova implementação e manifesto; apresentar hash exato, conteúdo, destino e orçamento ao PO. |
| C6 — executar e revisar | C5 e autorização específica | Uma campanha supervisionada; preservar falhas e pedir julgamento das novas saídas. Não transferir os aceites de respostas anteriores. |

Proposta de limites para C1, sujeita ao pedido final: até **16 invocações
sequenciais**, análise v4 e auditoria v5 por caso; até **180 s por chamada**,
reserva de limpeza de até **20 s por etapa** dentro de um prazo **global de
3.600 s**. Limites de transporte: entrada de 1 MiB e saída de 4 MiB por worker.
A sequência segue a ordem do manifesto revisado, sem concorrência. O controlador
deve recusar iniciar uma etapa quando não houver saldo de tempo para execução e
limpeza. O tempo concedido ao worker não pode reiniciar o prazo da campanha.

O destino proposto continua assinatura ChatGPT/Codex CLI, modelo solicitado
`gpt-6.1-sol`, sem API paga por chave. O pedido final deve vincular essa escolha;
ela não demonstra identidade remota autenticada ou qualificação do modelo.
Contamos invocações controladas pelo harness, sem prometer contabilizar chamadas
internas invisíveis do CLI.

Parar na primeira falha técnica, sem retry, repair, fallback ou retomada. Um
resultado de negócio `blocked` válido não é falha técnica. Falhas semânticas são
julgadas posteriormente e permanecem registradas; sucesso de transporte ou
parecer do auditor não concede PASS. Um processo cancelado precisa encerrar seus
descendentes e fechar o orçamento antes de devolver controle.

Enviar ao provedor somente fontes públicas de cada projeto e, na auditoria, sua
análise gerada. Não enviar expectativas, rubrica, julgamentos ou dados de outros
casos. Sem leitura de assets, reservado, ferramentas, web, treinamento, alteração
de defaults ou execução do código produzido. Saídas e journals ficam privados;
documentação pública contém metadados, limites e conclusões verificadas.

As tarefas C1–C5 estão **pendentes de implementação**. Esta entrega congela o
corpus e registra o plano; não acrescenta um controlador global funcional.
AHC-021/022 e Sprint 2.6 continuam em andamento. Não há qualificação do modelo,
autorização de compilação ou chamadas novas neste incremento.
