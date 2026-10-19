# Revisão de dependências — 2026-10-19

Decisão DE-0009: integrar os cinco updates abertos após revisar diffs, notas oficiais
e matriz CI de cada head atualizado sobre a `main`. Sem ampliação de permissões da
CI, nova dependência direta ou mudança nas faixas de compatibilidade do projeto.

| PR | Alteração | Motivo e risco verificado |
|---|---|---|
| [35](https://github.com/leozitogs/ai-harness-compiler/pull/35) | checkpoint-sqlite 3.1.2; checkpoint 4.3.0 | correções de persistência e replay; testes do adapter opcional preservam gates e retomada |
| [38](https://github.com/leozitogs/ai-harness-compiler/pull/38) | Pydantic 2.14.1; core 2.50.1 | compatibilidade de contratos exige schemas e tipagem sem drift; Python suportado continua 3.12+ |
| [37](https://github.com/leozitogs/ai-harness-compiler/pull/37) | LangGraph 1.2.15; SDK 0.4.8 | correções de execução; framework permanece restrito ao adapter opcional de equipe |
| [36](https://github.com/leozitogs/ai-harness-compiler/pull/36) | Ruff 0.17.1 | atualização de ferramenta de desenvolvimento; lint e formatação verificados |
| [29](https://github.com/leozitogs/ai-harness-compiler/pull/29) | setup-uv 10.3.0 | action permanece pinada por SHA, `contents: read` e executável uv 0.12.3 |

Notas primárias consultadas: [Pydantic](https://github.com/pydantic/pydantic/releases/tag/v2.14.1),
[LangGraph](https://github.com/langchain-ai/langgraph/releases/tag/1.2.15),
[Ruff](https://github.com/astral-sh/ruff/releases/tag/0.17.1) e
[setup-uv](https://github.com/astral-sh/setup-uv/releases/tag/v10.3.0).
Cada PR passou em conventions e Python 3.12/3.13, Linux/Windows, após atualização
da branch. Integração por squash, sem ignorar proteção ou usar merge administrativo.

No incremento AHC-022, repetir a suíte com todos os extras e o lock consolidado,
além de schemas, memória, tipagem e build. Resultados de CI e testes determinísticos
não qualificam um modelo. Não houve alteração de licença do projeto; os updates
não introduzem licença nova declarada, sem pretensão de auditoria jurídica completa.
