# Repositório e configuração GitHub

Repositório: [leozitogs/ai-harness-compiler](https://github.com/leozitogs/ai-harness-compiler).

**Repository name**

```text
ai-harness-compiler
```

**Display name**

```text
AI Harness Compiler
```

**Description**

```text
Compile project intent into typed, verifiable AI engineering harnesses: architecture, context, prompts, skills, tools, workflows, guardrails, and evals.
```

A description descreve a visão do produto; o README delimita o estágio atual.

**Topics sugeridos**

```text
ai-engineering, harness-engineering, compiler, llm, agentic-ai,
context-engineering, evals, mcp, python, pydantic
```

## Clonar e configurar

```sh
git clone git@github.com:leozitogs/ai-harness-compiler.git
cd ai-harness-compiler
uv sync --locked
git config core.hooksPath .githooks
```

Licença: Apache-2.0. A publicação inicial é bootstrap; mudanças seguintes passam por PR.

## Configuração operacional pretendida

Branch padrão `main`; squash habilitado; merge commits e rebase merge desabilitados;
exclusão automática de branches integradas. Proteção: CI e conventions obrigatórios,
resolução de conversas, sem force push ou deleção de main. Com mantenedor único,
zero aprovações obrigatórias; elevar para uma quando houver revisor independente.

As configurações reais podem ser consultadas no GitHub. Este documento não é
enforcement automático: editar o texto não altera proteções remotas.

```sh
git switch main
git pull --ff-only
git switch -c feat/ahc-001-canonical-intake
```

Siga [workflow](engineering/workflow.md), [backlog](product/backlog.md) e
[Definition of Done](delivery/scrum.md). Nenhuma tag de release ou publicação no
PyPI é disparada automaticamente pelo bootstrap.
