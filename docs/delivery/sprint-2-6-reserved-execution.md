# Sprint 2.6 — Executor e pedido concreto do reservado v2

Implementação e preparação offline concluídas no escopo do próximo passo pedido
pelo PO. Não houve leitura dos oito casos pelo autor do candidato nem chamadas
de avaliação. O aceite das expectativas do PR #63 permanece vinculado ao corpus
original; o orçamento abaixo é proposto, não autorizado.

## Pedido para decisão do PO

Arquivo: `evals/understanding/v2/reserved-execution/request.json`.
Digest canônico do pedido:
`a28e606595329ca1ed08bac8d036596f11226f3f9fe47251071baa42018f5872`.

| Campo | Escopo proposto |
| --- | --- |
| Corpus | Oito casos novos e expectativas já aprovadas; um ensaio por caso |
| Destino | Codex CLI pela assinatura ChatGPT, modelo solicitado `gpt-6.1-sol` |
| Receita | Análise v3.4 e auditoria consultiva v4.1; candidato congelado antes da curadoria |
| Invocações | No máximo 16: uma análise e uma auditoria por caso, sequenciais |
| Prazo | 180s por chamada, reserva de até 20s de limpeza; sessão de até 3.600s, incluindo preflight privado e limpeza |
| Falhas | Parar na primeira falha; nenhum retry, repair, fallback ou retomada automática |
| Conteúdo enviado | Apenas fontes sintéticas dos projetos aprovados e, na auditoria, análise gerada e suas fontes; nunca expectativas ou aprovações |
| Assets e ferramentas | Não ler assets; ferramentas e web desabilitadas pelo adapter congelado |
| Resultados | Diretório privado `.factory/reserved-v2-executions/reserved-v2-20261021-01/`; revisão humana das novas saídas posterior |
| Exclusões | Sem API paga por chave, treinamento, otimização no reservado, alteração de defaults ou aceite de história/modelo |

`model_invocations_charged` conta débitos do host, não requests observados no
backend; operações internas remotas permanecem desconhecidas. Perfil solicitado,
fontes do candidato e novas fontes do executor integram o digest. Metadados
imutáveis do modelo, sampler, custo e recursos continuam desconhecidos. Isso não
conclui AHC-024 nem garante repetibilidade determinística do serviço remoto.

## Verificação e próximos gates

Os testes usam somente workspaces sintéticos e geradores falsos. Cobrem execução
completa, falhas antes/depois do débito, limite de tempo, alteração de orçamento/
fontes, autorização stale, consumo único, integridade cruzada e revisão humana
separada. O pedido real foi preparado somente por metadados e fontes públicas;
nenhum arquivo de autorização real foi criado.

Depois de decisão específica do PO sobre esse pedido, registrar a autorização
vinculada ao digest exato; somente então executar. A primeira falha pode encerrar
antes das 16 invocações; não trocar código, parâmetros ou casos para insistir no
mesmo reservado. Reconciliar resultados, preservar toda a evidência privada e
encaminhar novas saídas ao julgamento humano dos seis critérios.

O wrapper reservado resolve a aprovação externa sem reescrever casos, hashes ou
contratos antigos. Sua avaliação fica `not-run`/`fail` até nova revisão das saídas;
auditoria consultiva não aprova análise. Resultado de integridade ou um caso
aprovado não qualifica modelo, autoriza compilação ou encerra a sprint.

AHC-021/022 seguem em revisão. Manual operacional:
[execução reservada](../engineering/reserved-evaluation-runs.md).
Decisão: [ADR-0029](../adr/0029-single-use-reserved-execution.md).

Posteriormente, em 21/10/2026, o PO autorizou o pedido acima. A execução parou
no preflight com zero invocações e foi encerrada sem retry. Os oito arquivos
originais estão intactos; os digests derivados não sobreviviam à normalização
numérica do contrato. [Diagnóstico e correção proposta](sprint-2-6-reserved-preflight.md).
O histórico de preparação acima permanece registrado; não é autorização de uma
segunda execução.
