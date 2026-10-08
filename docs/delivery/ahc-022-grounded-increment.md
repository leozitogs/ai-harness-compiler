# AHC-022 — Incremento de análise fundamentada

Entregue para revisão: contratos de análise/disposição, Protocol independente,
adapter Ollama, programa grounded-analysis/v1 versionado por texto e schemas,
modo opcional no runner supervisionado e diagnósticos fixos sem dados privados.

Verificação local: 412 testes sem skips, 31 novos casos; lint, formatação, mypy,
schemas, AGENTS, planos das três sprints e build passaram. Baseline/candidate SHA
continuam compatíveis e os dois journals antigos são legíveis. Nenhuma dependência
foi adicionada; avisos Apache-2.0 preservados.

Dois smokes reais ficaram limited/error, com uma tentativa e um caso not-run cada.
O primeiro erro genérico motivou diagnósticos seguros. O segundo foi rejeitado por
criterion-rule-link-invalid. Journals consistentes, sem proposta aceita, avaliação
semântica realizada ou conteúdo privado do provider salvo. Ver documentação e
artefatos de 2026-10-08. Não foi feito benchmark, comparação pareada ou holdout.

Rubrica/expectativas permanecem propostas aguardando revisão do PO. Nenhum aceite,
qualificação, encerramento de história ou dependência semanticamente atendida é
inferido deste incremento. INC-0007 continua aberto.

Próximo incremento: diagnósticos suficientes para repair limitado com tentativas
contabilizadas, comparação no development e revisão das classificações/fontes.
Toda chamada deverá consumir budget explícito; não esconder retries dentro do worker.
