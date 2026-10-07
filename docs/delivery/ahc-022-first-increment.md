# AHC-022 — Primeiro incremento preparatório

Entregue para revisão: extração determinística de declarações e verificação de
citações, CLI offline, dois schemas aditivos e reprodução da omissão nos pilotos.
Referência: ADR-0013 e docs/engineering/literal-grounding.md.

Verificação local: 381 testes, sem skips; 25 casos novos de grounding. Ruff check,
formatação, mypy, schemas, AGENTS e três planos de sprint passaram. Os dois
relatórios preservados mostram 0/4 critérios citados por BusinessRule extraída.
Nenhuma nova chamada ao modelo, alteração do prompt, tuning ou execução de holdout.

AHC-021 teve PR #20 integrado com CI verde. A rubrica e as expectativas continuam
aguardando revisão do PO. O trabalho preparatório da AHC-022 não encerra essa
dependência, não marca design/implementação completa nem qualifica modelos.

Ainda faltam análise consumindo os átomos, prompt versionado, verificação de
suporte/condition/outcome e repair limitado. Depois, comparar desenvolvimento,
congelar candidato e avaliar holdout com revisão humana e repetições previstas.
INC-0007 continua aberto: este incremento torna a ausência verificável, mas não
demonstra melhoria de entendimento. Source references não são prova de verdade.
