# Sprint 2.6 — diagnóstico e candidato v4.2

## Escopo executado offline

O PO autorizou seguir a sequência recomendada após os quatro julgamentos parciais.
Implementamos categorias sanitizadas de falha do worker, inspeção estrutural de
perguntas de precedência e um novo candidato explícito. A autorização permite
engenharia e preparo; não concede orçamento para novas chamadas.

Plano e verificação:

| Etapa | Dependência | Verificação |
|---|---|---|
| Preservar históricos | Julgamentos v4.1 registrados | Arquivos e digests originais intactos; arquivos históricos de código e replay congelado. |
| Diagnosticar worker | Contrato WorkerDiagnostic/v1 | Categorias fixas, erros desconhecidos, ausência de mensagens brutas, processo contido e parada sem retry. |
| Tratar precedência | Contrato ConflictQuestionDiagnostic/v1 | Omissão, um lado só, impacto inadequado, pergunta com todos os lados, análise sem conflito e adulteração do diagnóstico. |
| Preparar candidato | Programas v4.0/v4.1 preservados | v4.2 opt-in; mesmos inputs, expectativas, schema de saída, auditoria e defaults. |
| Preparar rodada | Source freeze estável e oito expectativas aprovadas | Pedido novo, todos os limites preservados, nenhuma autorização ou execução criada. |

## Observações, sem nova inferência

A inspeção das quatro análises já expostas identifica missing-question somente
no conflito, preservando seu FAIL humano. As outras três não apresentam conflito;
isso não acrescenta novos aceites. A receipt histórica exit 2 continua unknown.
Metadados públicos: `docs/evidence/sprint-2-6-v42-preparation-20261028/offline-diagnostics.json`.
Relatórios com análise integral permanecem em `.factory/v42-offline-diagnostics/`.

O v4.2 orienta a preservar conflitos genuínos e emitir pergunta explícita com
impact=precedence, citando todos os lados. Não escolhe uma regra, fabrica dúvida
de identidade, corrige automaticamente output ou acrescenta gates de aprovação.
O diagnóstico estrutural é separado do assessment histórico e do juiz humano.

## Pedido preparado, ainda sem autorização

Pedido: `evals/understanding/v4/development-candidate-v42/request.json`.
Protocolo: `evals/understanding/v4/development-candidate-v42/protocol.json`.
Digest canônico:

`20684db385afc73a5d9326d9946369e76284b4a8a60e199cefe77f7fcdc3a12a`.

- Oito casos públicos e expectativas já aprovados, sem editar manifesto ou rubrica.
- Uma análise v4.2 e uma auditoria v5 por caso; saída SemanticAnalysis/v4.
- Modelo solicitado gpt-6.1-sol pela assinatura ChatGPT/Codex CLI.
- Teto global de 16 invocações sequenciais e 3.600 segundos para a sessão inteira.
- Até 180 segundos por chamada, com reserva de limpeza de até 20 segundos por etapa.
- Até 1 MiB de entrada e 4 MiB de saída por worker; 107 arquivos no source freeze.
- Parar na primeira falha técnica; sem retry, repair, fallback, concorrência ou retomada.
- Enviar somente fontes públicas do projeto e, à auditoria, a análise recém-gerada.
  Sem expectativas, rubrica, julgamentos, outros outputs, assets, reservado,
  ferramentas, web, API paga por chave, treinamento ou alteração de defaults.
- Journals privados novos em `.factory/semantic-v4-campaigns/dev-v42-20261028-01/`
  e oito fluxos aninhados `.factory/semantic-v4-runs/dev-v42-20261028-01-01/` até `-08/`.

Os orçamentos anteriores estão encerrados. Expectativas aprovadas não autorizam
execução; julgamentos antigos não aprovam saídas novas. Supervised/Campaign gates
continuam exigindo autorização do pedido exato antes de claim ou lançamento.

## Pendências e critérios de saída

Verificação local: 57 testes focados passaram na primeira execução válida.
A suíte completa terminou com 1.384 PASS e um erro de setup (`MemoryError` em
`intake.stream.read`, ao carregar a fixture pública de
`test_recorded_late_call_remains_error_not_success`). O teste isolado junto aos
contratos novos passou: 41 PASS, sem alterar código ou limites. Build, checks
estáticos, schemas e replays históricos passaram. A causa da alocação não foi
estabelecida; `INC-0034` registra a ocorrência sem atribuí-la ao hardware.
A CI completa permanece gate de integração; nenhum teste foi ignorado.

A suíte offline e o build verificam implementação, não eficácia de prompt/modelo.
Depois de autorização específica, executar uma rodada, verificar integridade,
inspecionar os diagnósticos sem alterar a resposta e submeter novas saídas ao PO.
Falhas técnicas, regressões e casos ausentes devem continuar visíveis. Não retomar
automaticamente uma campanha interrompida. Novas categorias melhoram diagnóstico
futuro, mas não demonstram a causa do incidente histórico.

INC-0031 e INC-0033 permanecem abertos. Nenhuma qualificação, autorização de
compilação ou conclusão de AHC-021/022 e da Sprint 2.6 é declarada.
