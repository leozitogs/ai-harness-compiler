"""Register legacy decisions and an observed regression without rewriting existing revisions."""

import hashlib
from pathlib import Path

from ai_harness_compiler.memory.store import MemoryStore
from ai_harness_compiler.models.memory import RecordDraft

root = Path(__file__).resolve().parents[1]
store = MemoryStore(root)


def evidence(source: str, note: str, outcome: str = "observed") -> list[dict[str, str]]:
    return [
        {
            "source": source,
            "note": note,
            "outcome": outcome,
            "sha256": hashlib.sha256((root / source.split("#", 1)[0]).read_bytes()).hexdigest(),
        }
    ]


def register(payload: dict[str, object], promote: bool = False) -> None:
    draft = RecordDraft.model_validate(
        {
            "project_id": "ai-harness-compiler",
            "author": "bootstrap:existing-project-evidence",
            **payload,
        }
    )
    if draft.id in store.latest():
        return
    record = store.add(draft)
    if promote:
        store.review(
            record.id,
            1,
            "active",
            "migration:documented-decision",
            "Imported the existing documented decision; no new PO approval claimed.",
        )


legacy = [
    (
        "ADR-0001",
        "docs/adr/0001-compiler-first.md",
        "Contratos antes de agentes",
        "Preservar o core Python/Pydantic com representações intermediárias verificáveis.",
    ),
    (
        "ADR-0002",
        "docs/adr/0002-reviewable-generation.md",
        "Geração revisável e instalação separada",
        "Exportar somente em pastas novas e separar integridade de avaliação do produto.",
    ),
    (
        "ADR-0003",
        "docs/adr/0003-governance-and-task-plans.md",
        "Governança e planos observáveis",
        "Usar Apache-2.0, branches curtas, Conventional Commits e TaskGraph validado.",
    ),
]
for identifier, source, title, decision in legacy:
    register(
        {
            "id": identifier,
            "kind": "ADR",
            "title": title,
            "summary": decision,
            "context": "Decisão pré-existente; conteúdo completo no documento de origem.",
            "decision": decision,
            "tags": ["architecture", "contracts", "engineering"],
            "evidence": evidence(source, "Original documented architectural decision."),
        },
        promote=True,
    )

register(
    {
        "id": "DOC-0001",
        "kind": "DOC",
        "title": "Concepção do AI Harness Compiler",
        "summary": "Referência do objetivo, usuários, hipóteses e fronteiras do produto.",
        "context": "Fonte documental do produto, sem duplicar todo o conteúdo no prompt.",
        "tags": ["product", "conception", "scope"],
        "evidence": evidence("docs/product/conception.md", "Existing project conception document."),
    },
    promote=True,
)
register(
    {
        "id": "DE-0001",
        "kind": "DE",
        "title": "Memória de engenharia versionada",
        "summary": "JSON por revisão como fonte de verdade; SQLite FTS5 como índice reconstruível.",
        "context": "Solicitação do PO; revisão desta nova decisão ainda pendente.",
        "decision": "Separar propostas, decisões e experiências com evidências e limites.",
        "alternatives": ["Markdown sem contratos", "Banco como única fonte de verdade"],
        "consequences": ["Revisões em Git", "Cache reconstruível", "Sem treino de pesos do LLM"],
        "tags": ["memory", "documentation", "learning"],
        "related": ["ADR-0001"],
    }
)
source = "tests/test_memory.py#test_argparse_runtime_failure_has_a_verified_reproduction_and_fix"
regression = evidence(
    source, "Regression reproduces TypeError and tests postponed annotations.", "passed"
)
register(
    {
        "id": "INC-0001",
        "kind": "INC",
        "title": "Importação da CLI falhou por anotação argparse",
        "summary": "TypeError: type '_SubParsersAction' is not subscriptable na importação.",
        "context": "Uma anotação aceita pelo type checker era avaliada em runtime.",
        "challenge": "A CLI deixou de importar ao adicionar um tipo genérico do argparse.",
        "root_cause": "O objeto do argparse não suporta subscrição em runtime no Python testado.",
        "attempts": ["Anotação direta _SubParsersAction[ArgumentParser] reproduziu a falha."],
        "resolution": "Adicionar from __future__ import annotations no módulo da anotação.",
        "tags": ["python", "argparse", "annotations", "regression"],
        "evidence": regression,
    }
)
register(
    {
        "id": "LES-0001",
        "kind": "LES",
        "title": "Tipos estáticos podem falhar em runtime",
        "summary": "Postergar anotações resolve este caso específico da CLI argparse.",
        "context": "Aprendizado derivado de INC-0001 e de uma regressão executada localmente.",
        "challenge": "Uma anotação interrompeu a importação de um módulo funcional.",
        "root_cause": "Sintaxe genérica que o objeto não implementa em runtime.",
        "resolution": "Usar from __future__ import annotations e verificar importação e CLI.",
        "lesson": "Verificar suporte em runtime ao introduzir anotações, além de executar mypy.",
        "applicability": ["Anotações de argparse._SubParsersAction nos módulos da CLI"],
        "limitations": [
            "Validado localmente em Python 3.13; não é solução universal para TypeError.",
            "Não altera expressões genéricas executadas fora de anotações.",
        ],
        "tags": ["python", "argparse", "annotations", "regression"],
        "related": ["INC-0001"],
        "evidence": regression,
    }
)
register(
    {
        "id": "RUN-0001",
        "kind": "RUN",
        "title": "Registrar e reutilizar uma experiência",
        "summary": "Captura, diagnóstico, validação e revisão antes de reutilizar uma solução.",
        "context": "Operação da memória pelo PO e colaboradores de código.",
        "procedure": [
            "Registrar incidente sem segredos",
            "Documentar causa, tentativas e solução",
            "Executar regressão",
            "Anexar evidência com digest",
            "Criar lição com limites",
            "Revisar explicitamente",
            "Atualizar índice e abrir PR",
        ],
        "tags": ["memory", "incident", "learning"],
        "related": ["DE-0001", "LES-0001"],
    }
)
(root / "knowledge/INDEX.md").write_text(store.render_index(), encoding="utf-8", newline="\n")
print(f"Memory bootstrapped: {len(store.latest())} records; existing revisions preserved.")
