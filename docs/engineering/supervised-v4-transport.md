# Operação do transporte v4 supervisionado

Integração opt-in; não altera factory, executor reservado ou adapter históricos.
Não executar com autorizações anteriores. [ADR-0032](../adr/0032-supervised-v4-transport.md)
explica a contenção, fundamentos e limitações.

## Plano e verificações

| Trabalho | Depende de | Verificação |
| --- | --- | --- |
| Contratos de limites e recibos | Fluxo v4 | Recusar expansões, status/observações contraditórios e autorização trocada |
| Supervisor de processo | Limites | Timeout, excesso de saída, falha de spawn e encerramento de descendente |
| Worker fixo | Supervisor | Validar antes de importar/instanciar provider; somente resposta final |
| Integração e congelamento | Contratos e worker | Gates antes do spawn; snapshot instalado/repositório; uso único; primeira falha encerra |
| Replay | Journals | Adulteração de claim, tentativa, recibo, resposta ou autorização recusada offline |
| Regressões e integração | Implementação | Schemas, checks completos, memória e CI; sem inferência real |

## Interfaces Python

`prepare_supervised_flow(repository, flow, limits)` captura metadados e retorna
SupervisedFlowRequest/v1. `flow` é SemanticFlowRequest/v4; `limits` declara prazo
por chamada (1..300s), limpeza (1..30s), sessão (até 3600s), bytes de entrada/saída
e duas invocações máximas. Esses intervalos são validação, não orçamento concedido.
O preparo não lê assets, chama CLI/provider ou cria autorização.

`run_supervised_flow(repository, request, authorization)` exige nova
SupervisedFlowAuthorization/v1 do hash exato. Aprovações de expectativas/rubrica
e compatibilidade do caso continuam necessárias. Autorizar execução não aprova
respostas, semântica ou compilação. O modelo solicitado permanece explícito, sem
fallback. Não mudar o comando fixo do worker com conteúdo de projeto ou modelo.

O supervisor envia somente modelo solicitado, prompt da etapa, response_schema e
timeout ao worker. Expectativas, rubrica e julgamentos ficam no processo principal.
O worker chama o adapter existente uma vez; login/status não é inferência e eventos
intermediários continuam descartados por esse adapter. O supervisor não conta as
requisições internas da CLI ou autentica a identidade real do modelo.

Os arquivos novos ficam em `.factory/supervised-v4-runs/<run_id>/` e claims em
`.factory/supervised-v4-claims/<request-sha256>.json`. O fluxo v4 mantém seu próprio
journal privado. Nunca publicar fontes, expectativas ou respostas privadas. Prompts
enviados ficam representados por hashes; erros brutos de provider/OS não são salvos.

`validate_supervised_flow(repository, run_id)` revalida fontes do pacote e lock,
comando/runtime declarados, relatório, projeção de autorização, journal v4, payloads,
recibos e respostas. É replay de integridade, sem inferência. Se as fontes mudaram,
o replay atual recusa: usar o checkout congelado correspondente. Não reescrever
freeze antigo para fazê-lo passar. Revisão humana de saída continua no assessment
v4 separado e não promove automaticamente o modelo.

## Significado dos resultados

O recibo registra tentativa, spawn e fatos observados de encerramento separadamente.
Um JSON válido de transporte pode falhar no contrato semântico depois: manter o
recibo de transporte bem-sucedido e a falha do fluxo. Exceder a sessão nunca produz
completed externo, mesmo que as duas etapas internas já tenham resultado técnico.

Não prometer prazo de tempo real, ambiente hermético, segurança contra código
hostil, observação de todos os descendentes ou número de requisições remotas.
Workers confiáveis são pré-requisito; o supervisor não executa artefatos gerados.
Interrupções podem consumir claim e deixar estado incompleto; não retomar.

## Próxima avaliação

Preparar proposta concreta de desenvolvimento com candidato/transportes congelados,
inputs públicos e novo orçamento/conteúdo/destino para revisão. Não reutilizar
aceites de expectativas v2/v3 como aprovação de outputs v4. Compatibilidade dos
schemas v4/v5 com o provedor, métricas semânticas e reservado novo continuam pendentes.
