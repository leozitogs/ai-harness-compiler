# AHC-022 — Incremento de verificação semântica v2

Data: 2026-10-09. Status: implementação para integração; história não concluída.

Entregues análise tipada v2, bindings por átomo, perguntas com impacto, disposição
derivada, segunda chamada de verificação e avaliação offline com revisão humana
separada. CLI: `analyze-project-v2`, `verify-analysis-v2`, `assess-analysis-v2`.
Rubrica v2 registra os critérios aprovados; expectativas individuais permanecem
em draft. Não há reinterpretação de corpus/relatórios v1 nem alterações em `study`.

## Evidência de execução

Duas chamadas reais via modelo principal `gpt-6.1-sol` e Codex CLI com assinatura
ChatGPT, sem tools, no caso público `dev-new-domain` do desenvolvimento v1. A análise
representou a obrigação de responsável/origem por publicação e sete conclusões de
contexto. O verificador retornou oito pareceres de suporte. Isso prova execução e
contratos válidos, não precisão semântica ou independência científica do modelo.

Arquivos em `docs/evidence/ahc-022-semantic-v2-20261009/`: `analysis.json`,
`advice.json`, `assessment.json`. Avaliação permanece **not-run**: não existe parecer
humano nem aprovação das expectativas individuais. Nenhum holdout foi executado.
Compilação permanece **not-authorized**, qualificação **not-established**.

## Revisão e validação

Agente independente encontrou omissão de subject/motivo da recusa no hash por
achado. Ambos foram preservados e cobertos por regressão; o hash global já protegia
a revisão humana. Testes incluem cobertura/support incompletos, parecer stale,
fontes trocadas, classificação/exceções alteradas, perguntas técnicas não bloqueantes,
conflitos dentro da mesma referência-pai e reordenação dos critérios.

Próximo gate: revisar expectativas e resultados de desenvolvimento v2 com o PO,
depois congelar corpus/programa e executar avaliação reservada. Blueprint AHC-020
continua dependente da qualificação do entendimento.
