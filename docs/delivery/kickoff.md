# Kickoff

Documento preparado em 2026-10-05. Reunião e início da Sprint 1 ainda não agendados.

## Objetivo

Alinhar a concepção, validar o Product Goal, revisar a baseline demonstrável e
confirmar capacidade e escopo de um primeiro incremento verificável.

## Responsabilidades propostas

- Leonardo / Product Owner: priorização, objetivo e aceitação de valor; confirmar no kickoff.
- Developers: dimensionar trabalho, elaborar plano e entregar qualidade; composição a confirmar.
- Scrum Master: facilitar processo e remover impedimentos; pessoa a definir.
- Assistência de IA: apoiar análise, implementação e verificação; não substituir accountability humana.

Em operação individual, registrar explicitamente a adaptação e buscar feedback
externo. Não apresentar uma equipe Scrum completa como existente sem essas definições.

## Pré-leitura e demonstração

Ler concepção, arquitetura, backlog, workflow de Git e Sprint 1.

```sh
uv sync --locked
uv run factory validate project-definition
uv run factory tasks project-definition --select ahc-001 ahc-002 ahc-003 ahc-004
uv run python scripts/generate_sprint_plan.py --check
uv run pytest
```

## Agenda proposta — 60 minutos

| Minutos | Discussão | Saída |
|---|---|---|
| 0–10 | Problema, usuários e Product Goal | Escopo e hipóteses alinhados |
| 10–20 | Demo e limites da baseline | Compreensão do que funciona |
| 20–35 | Backlog, riscos e critérios | Ordenação inicial revisada |
| 35–45 | Engenharia, licença, fluxo Git e DoD | Acordo de trabalho |
| 45–55 | Capacidade e proposta de Sprint 1 | Escopo e objetivo ajustados |
| 55–60 | Decisões e próximos passos | Responsáveis e pendências |

## Decisões a registrar

Data inicial, disponibilidade real, responsáveis, necessidade de reduzir escopo,
stakeholder da Review, exemplos de projeto e canal de impedimentos. Não antecipar
aprovações ou registrar presença que ainda não ocorreu.

## Saída esperada

Sprint Goal confirmado, Sprint Backlog selecionado pelos Developers, plano de
trabalho ajustado, Definition of Done compreendida e agenda de eventos acordada.
O manifesto da sprint só muda de `proposed` depois dessas decisões.
