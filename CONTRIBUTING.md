# Contribuindo

Este projeto começa pela especificação e pelas avaliações. Mudanças devem conectar
um requisito a um contrato e a uma forma de verificação.

## Ambiente

```sh
uv sync --locked --all-extras
uv run factory validate examples/project-definition
```

Código e identificadores em inglês; documentação explicativa em português.
Não usar provedores externos ou chaves reais nos testes padrão.

## Antes de abrir um PR

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run python scripts/export_schemas.py --check
uv run python scripts/generate_repo_agents.py --check
uv run python scripts/generate_sprint_plan.py --check
uv build
```

Ao alterar modelos, regenere schemas. Ao alterar `docs/repository-policy.json`,
regenere `AGENTS.md` com `uv run python scripts/generate_repo_agents.py`.
Mudanças arquiteturais precisam de um ADR em `docs/adr/`.

Descreva comportamento, validação e limites no PR. Não apresente planos de evals
como resultados; não adicione camadas vazias apenas para antecipar o roadmap.
Novos efeitos colaterais devem ter fronteiras e permissões explícitas.

## Dependências

Use `uv add` / `uv add --dev` e versione `uv.lock` junto com `pyproject.toml`.
Integrações futuras ficam em adapters; bibliotecas de agentes não invadem os contratos.

## Fluxo de trabalho

Leia [commits e branches](docs/engineering/workflow.md) e a
[Definition of Done](docs/delivery/scrum.md). Ative o hook local:

```sh
git config core.hooksPath .githooks
```

Use branches como `feat/ahc-001-canonical-intake`, Conventional Commits e PRs com
evidências. Contribuições intencionais seguem Apache-2.0, conforme [LICENSE](LICENSE).
Critérios de produto vivem em `project-definition/project.yaml`; após alterar
escopo ou critérios da Sprint 1, regenere `planning/sprint-1.tasks.json`.
