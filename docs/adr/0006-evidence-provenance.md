# ADR-0006 — Proveniência explícita e IR v2

Estado: adotada na implementação da AHC-003; incremento sujeito à revisão por PR.

## Contexto

Evidence/v1 tinha apenas ID, source, claim e kind. Referências podiam resolver um
ID correto que pertencia a outra capacidade. Não havia estado de revisão, origem
da fonte ou método de verificar integridade da declaração normalizada.

Critérios: AHC-003 em `project-definition/project.yaml`; contrato anterior no
snapshot `tests/fixtures/harness-v1.json`.

## Decisão

Separar cadastro de fontes de afirmações e usar escopos estruturais. Gerar um
digest do input canônico determinístico; pesquisa fornecida é metadata offline.
Versionar DNA e HarnessSpec para v2, com migração explícita de declarações da
baseline v1, sem inventar proveniência ausente. Manter o core sem providers.

## Alternativas e consequências

Campos opcionais inferidos em Evidence/v1 evitariam migração, mas deixariam fontes
incompletas e alterariam silenciosamente o significado de referências existentes.
Buscar fontes durante o planejamento adicionaria efeitos e impediria baseline
offline/reprodutível. Por isso não adotamos essas alternativas.

Consumidores da IR precisam migrar. Metadados verified são declarações rastreáveis,
sem autenticação ou validação independente pelo compilador. Evals e adapters
posteriores deverão testar a substância de fontes e decisões.
