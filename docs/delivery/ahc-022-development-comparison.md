# AHC-022 — Comparação inicial em development

Comparação observacional em 2026-10-08, mesmo Qwen3 Instruct/hash, código, corpus,
8k de contexto e saída até 4096 tokens. Oito casos congelados, uma repetição por
programa, oito tentativas por sessão, timeout=180 s e sessão=1800 s. Baseline
executada antes de compact. Journals completos e validados; nenhum holdout.

| Caso | Baseline | Compact | Regras propostas no compact |
|---|---|---|---|
| Novo domínio | error | completed / eval not-run | 1 |
| Regras A | completed / eval fail | completed / eval not-run | 1 |
| Regras B | completed / eval fail | completed / eval not-run | 1 |
| Conflito de branding | completed / eval fail | error | — |
| Ambiguidade | error | completed / eval not-run | 1 |
| Regras compatíveis | error | completed / eval not-run | 4 |
| Assets não lidos | completed / eval fail | error | — |
| Input adversarial | error | completed / eval not-run | 1 |

Baseline: 4/8 propostas formalmente válidas, todas com zero BusinessRule; quatro
erros e quatro eval fail. Compact: 6/8 formalmente válidas, todas com regras
origin=hypothesis e eval not-run; dois compact-analysis-invalid. Saída rejeitada
não foi persistida, portanto o código desses erros não identifica a causa exata.

O ganho observado é aceitação estrutural e presença de regras propostas, com
citações montadas pelo compilador. Não estabelece que a interpretação por posição,
condição/resultado, domínio, conflitos ou perguntas estejam corretos. Os dados
não autorizam qualificar modelo, aprovar rubrica ou encerrar a história.

No smoke compatível, há suporte semântico inadequado: o domínio cita restrições
técnicas e notas tratam critérios explícitos como implícitos. Preservamos esse
achado para revisão; uma correção de representação não o remove automaticamente.

Tempos totais observados: baseline 150,008 s, compact 81,471 s. Uma repetição,
ordem fixa e cache não controlado impedem ranking robusto ou atribuição causal
da diferença. Não estimar custo/tokens de propostas rejeitadas a partir de zero.

Fontes: docs/evidence/ahc-022-development-baseline-20261008 e
docs/evidence/ahc-022-development-compact-20261008. O resumo JSON inclui hashes dos
relatórios, corpus, modelo e código observados; é uma observação derivada destes
journals, não um novo contrato de benchmark ou prova autenticada de execução.

Próximos passos: revisão das expectativas/rubrica com PO, análise dos dois erros
compactos sem relaxar contratos e comparação de modelos/perfis com repetições.
INC-0007 e a qualificação permanecem pendentes.
