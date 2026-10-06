# AHC-001 — Evidências locais de implementação

Execução em 2026-10-06, Windows, Python 3.13.7, extras de equipe instalados.

Comando de regressão:

```sh
.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --basetemp .factory/intake-full-1
```

Resultado observado: **111 passed in 13.75s**, sem skips. Ruff lint, formatação
e mypy também passaram. Não extrapolar este resultado para Linux ou Python 3.12;
a matriz de CI verifica esses ambientes separadamente.

## Critérios da história

| Critério | Evidência local |
|---|---|
| Duplicatas, limite configurado, versões desconhecidas e diagnóstico estável | `tests/test_intake.py`: parametrização de rejeições e limites por bytes, código API/CLI |
| UTF-8 e referências válidas sem execução/rede | BOM/Unicode aceitos; spy restringe leitura ao manifesto, socket bloqueado; tag Python rejeitada |
| Casos válidos e inválidos em Linux e Windows | Windows local aprovado; jobs Linux/Windows 3.12/3.13 necessários para o gate remoto |

## Incidente no teste de quantidade de nós

O identificador automático de pytest incorporava um payload com 50.001 escalares.
O caso falhou em setup/teardown no Windows, antes de avaliar o comportamento do
loader. Reprodução isolada, removendo os IDs explícitos e selecionando
`INTAKE_YAML_NODES`, confirmou:

```text
os.environ[var_name] = value
ValueError: the environment variable is longer than 32767 characters
```

A correção usa IDs curtos explícitos (`case-0` a `case-17`), mantendo os payloads
originais e as verificações. A suíte passou após a correção. Aplicabilidade:
fixtures parametrizadas grandes em pytest no Windows; não confundir esse limite
de variável de ambiente com tamanho de manifesto ou segurança do produto.

Esta evidência comprova execução local de checks, sem declarar aprovação do PO,
integração da branch ou eval do harness gerado.
