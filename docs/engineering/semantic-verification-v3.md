# Verificação de fontes e omissões v3

O comando `factory verify-analysis-v3 analysis.json --output advice-v3.json` usa
a política principal por chamada explícita, sem fallback ou execução de tools.
V2 permanece disponível. Arquivo existente não é sobrescrito. A análise original
é preservada; o parecer não autoriza compilação nem substitui revisão humana.

O protocolo v3 mantém os julgamentos dos achados e adiciona:

- `omissions`: regras, perguntas materiais ou conflitos ausentes, com fonte exata;
- `source_coverage`: uma linha para cada átomo, incluindo hash da quote original,
  achados representados e omissões associadas.

Uma fonte parcialmente representada pode conter ambos os vínculos. Fontes
classificadas como ignoradas não reivindicam representação ou omissões. Perguntas
omitidas exigem impacto em regra, autorização, resultado ou precedência. Conflitos
exigem dois átomos distintos, mesmo que compartilhem a referência-pai.

Snapshots, achados, omissões, quotes e inventários são validados novamente na
desserialização. Fontes trocadas, hashes stale, duplicações e referências inexistentes
são rejeitados. Isso valida o contrato, não a pertinência semântica da classificação.
`semantic_status` e `model_qualification` continuam `not-established` mesmo sem omissões.

Não passar expectativas dos casos ao auditor. Uma omissão proposta é diagnóstico:
deve ser examinada antes de corrigir ou regenerar a análise. O host não transforma
recusa em `ready` e não promove relatório LLM a `SemanticHumanReview`.

A geração continua em `SemanticAnalysis/v2`, com programa `semantic-analysis/v2.2`.
O contrato não mudou; o programa explicita preservação da intenção legítima após
ignorar instruções adversariais e investigação de decisões materiais indefinidas.
Relatórios históricos mantêm seus resultados; a emenda usa novas evidências.
