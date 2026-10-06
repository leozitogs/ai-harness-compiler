# AHC-003 — Evidências de implementação

Execução local em 2026-10-06: Windows, Python 3.13.7, todos os extras instalados.
Suíte completa: **145 passed in 9.99s**, sem skips. Ruff lint/formatação, mypy,
schemas e TaskGraph também passaram. A matriz de CI remota deve aprovar Linux e
Windows, Python 3.12 e 3.13, antes da integração.

```sh
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp .factory/evidence-full-3
```

| Critério de aceitação | Evidência |
|---|---|
| IDs, origem, digest opcional, estado e coleta quando aplicável | SourceRecord valida digest e timestamps, metadados de revisão e ordem temporal; baseline gera snapshot sem inventar verificação |
| Referências ausentes, duplicadas e incompatíveis rejeitadas | Testes de fonte, capacidade, domínio e decisão; rejeição antes de criar saída; mutação de digest/afirmação canônicos bloqueada |
| Declaração vs pesquisa externa distinguíveis sem pesquisa automática | EvidencePack fornecido atravessa input→DNA→grafo→bundle com socket bloqueado; pesquisa não pode fingir declaração de domínio |

`tests/test_evidence.py` também exercita migração explícita do snapshot real v1
em `tests/fixtures/harness-v1.json`, roundtrip JSON, schemas, preservação do arquivo
existente e ausência de invenção de proveniência para evidências customizadas.

## Aprendizado de portabilidade

Um teste leu o JSON exportado com `Path.read_text()` sem encoding explícito. No
Windows, textos UTF-8 com acentos foram interpretados pelo encoding padrão e a
comparação falhou. A produção já escrevia UTF-8; a correção foi especificar
`encoding="utf-8"` no leitor do teste, preservando comparação de conteúdo real.
Regressão completa passou após a correção. Isso não permite afirmar que todos
os demais leitores externos já são portáveis.

Os checks validam contratos e exportação, sem autenticar reviewers, obter fontes
externas ou provar a verdade científica de afirmações. Evals do produto gerado
continuam `not-run`.
