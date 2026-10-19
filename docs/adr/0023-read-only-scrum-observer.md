# ADR-0023 — Observação Scrum separada de aceite e operação

Status: aceito para implementação em 2026-10-19; AHC-027, DE-0011.

## Decisão

Adicionar contratos provider-independent `DeliveryEvidence/v1`, `ScrumObservation/v1`,
`Impediment/v1` e `SprintSnapshot/v1`. Capturar conteúdo, hash, escopo e horário de
coleta. O snapshot recalcula fatos e diagnósticos ao desserializar. Alterar apenas
fatos, diagnósticos ou hash é rejeitado.

Precedência por campo: manifesto validado fornece identidade, critérios e dependências;
plano fornece seleção, estado declarado e declaração do resultado do objetivo;
GitHub fornece lifecycle observado de issues/PRs e checks reportados naquele head.
Estado remoto não substitui estado declarado ou aceite. Work-items são verificados
contra sprint/seleção. Política Scrum e índice de memória são referências, não regras
executáveis nem certificados de que todos os critérios foram revisados.

Vínculo story→issue vem do tracking com URL exata; story→PR é explícito, nunca
inferido de título ou texto. Divergência é preservada. Fonte ausente, antiga, ambígua
ou fora de escopo não fornece fato atual. TTL incide sobre coleta, não sobre a data
da última mudança de uma issue: um objeto antigo pode ter sido observado agora.

Coletores ficam fora do modelo: leitura local limitada e GitHub opt-in via comandos
fixos de leitura do `gh`, sem shell, body de issue, credenciais, escrita remota ou LLM.
Parser puro de manifesto é extraído do intake para normalizar os mesmos bytes
capturados; isso evita ler uma revisão e identificar outra com seu hash.

## Limites

`acceptance=not-established` e `completion_authority=none` são constantes. Check success
não certifica required-check policy nem semântica; PR merged/issue closed não certificam
DoD. `declared_goal_outcome` é declaração do plano, não avaliação do agente.

Checksum verifica consistência, não autenticidade ou verdade de quem produziu um
snapshot. `reconcile` valida snapshot anterior e reavalia freshness no horário atual,
offline; não atualiza fontes. Recoleta exige `observe` explícito. Não há daemon,
cache persistente, monitoramento ou retomada de escrita.

Integração procedural no Nexo/LangGraph pertence à AHC-028; operações autorizadas e
journal, à AHC-029. Não acoplar coleta à geração de decisões ou compilação de harness.
