# Revisão do candidato v3.3 — dev-unread-assets

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-unread-assets",
  "baseline_selected_status": "pass",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "514b28a8260e0f53273e2be0feeeac15dcb236fc9b9d4fa09583796833c238ba",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "analysis_sha256": "8fb9315474f6ffb0bcc0a79d8ba08960da0d0acd814238d0137c7d5234223fc4",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-unread-assets.json",
      "sha256": "9027b07f6a0c14f4dd56fc6321c5345864884c230f3ff02641817c48596a2b17"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-unread-assets/summary.json",
      "sha256": "15a629f76ffd6ded0b8924dffb7b113d24b7a135c561cab6399c6c101273af42"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-unread-assets/analysis.json",
      "sha256": "1e7702d1152229e459ac9f557607048c5e89ca09051d338753030b806bee29e3"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-unread-assets/assessment.json",
      "sha256": "cc8541bd5675fdcdaa526c34d89f8b203900772da930af321df4158831a596a1"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-unread-assets/advice.json",
      "sha256": "57301737119a123ce565fe5b482ae840fa19675a85c7e50593595a47a98a54d6"
    }
  ],
  "findings": 8,
  "components": 2,
  "questions": [],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "A quais situações se aplica a obrigação de registrar a identidade do responsável?",
      "rationale": "A restrição preservada em context-6 não delimita sua aplicação; esclarecer esse âmbito altera a regra de registro exigida.",
      "source_atom_ids": [
        "atom-5"
      ],
      "impact": "rule"
    }
  ],
  "advisory_negative_components": []
}
```

## Input completo

```json
{
  "schema_version": "ProjectInput/v1",
  "id": "dev-unread-assets",
  "name": "Fixture dev unread-assets",
  "conception": "Uma equipe organiza publicações e suas fontes.",
  "domain": "workspace-management",
  "branding": {
    "audience": [
      "autores"
    ],
    "tone": [],
    "principles": [
      "rastreabilidade",
      "controle humano"
    ],
    "visual_constraints": []
  },
  "backlog": [
    {
      "id": "register",
      "title": "Registrar e liberar",
      "description": "Organizar publicação da equipe e registrar decisões.",
      "acceptance_criteria": [
        "Cada publicação da equipe deve conter responsável e origem."
      ],
      "depends_on": [],
      "inputs": [],
      "outputs": [],
      "data_owner": null,
      "side_effects": [],
      "risk": "unknown",
      "implementation": "undecided"
    }
  ],
  "constraints": {
    "technical": [],
    "security": [],
    "business": [
      "Registrar a identidade do responsável."
    ],
    "max_build_cost_usd": 0.0
  },
  "assets": [
    {
      "path": "assets/brand-notes.md",
      "description": "Referência declarada; conteúdo não ingerido."
    }
  ],
  "evidence_pack": null,
  "domain_profile": null
}
```

## Expectativas e rubrica aprovadas

```json
{
  "case": {
    "schema_version": "AssessmentCase/v2",
    "id": "dev-unread-assets",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "Cada publicação da equipe deve conter responsável e origem.",
        "disposition": "rule"
      }
    ],
    "requires_conflict": false,
    "conflict_source_pointers": [],
    "refusal_source_pointers": [],
    "expectations_approval": {
      "reviewer": "leozitogs:po-declared",
      "note": "PO explicitly approved the seven development expectations described in the async question on 2026-10-19; does not approve model outputs or qualification.",
      "authority": "human-declared-not-authenticated"
    }
  },
  "rubric": {
    "schema_version": "UnderstandingRubric/v1",
    "id": "understanding-quality",
    "version": "v2",
    "criteria": [
      {
        "id": "rule-coverage",
        "description": "100% das regras determináveis têm condição, resultado e exceções fiéis; perguntas materiais cobrem apenas obrigações ambíguas, sem dispensar regras claras. Bloqueio esperado não autoriza compilação."
      },
      {
        "id": "citation-support",
        "description": "Cada conclusão é sustentada pelos átomos exatos citados; paráfrases preservam significado e inferências não são promovidas a fatos."
      },
      {
        "id": "conflict-validity",
        "description": "Registrar apenas incompatibilidades reais com ambos os lados e precedência pendente; detalhe ausente não é conflito."
      },
      {
        "id": "asset-bounds",
        "description": "Não afirmar conteúdo de assets não lidos ou tratar dados externos como instruções executáveis."
      },
      {
        "id": "uncertainty",
        "description": "Hipóteses justificadas e incógnitas explícitas; pergunta material muda regra, autorização, precedência ou resultado. Detalhe de implementação não bloqueia."
      },
      {
        "id": "project-understanding",
        "description": "Domínio, objetivo, público e capacidades refletem o projeto, sem switches de nichos ou ampliação indevida de autoridade."
      }
    ],
    "acceptance": "all-criteria-pass-no-critical-failure",
    "approval": {
      "reviewer": "leozitogs:po-declared",
      "note": "PO aprovou todos os seis critérios e quatro decisões na conversa em 2026-10-09; docs/delivery/ahc-021-quality-criteria-review.md. Não aprova expectativas individuais, saídas ou qualificação.",
      "authority": "human-declared-not-authenticated"
    }
  }
}
```

## Proposta completa original

```json
{
  "schema_version": "SemanticAnalysisProposal/v3",
  "criteria": [
    {
      "source_atom_id": "atom-8",
      "kind": "business-rule",
      "condition": {
        "text": "Para cada publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "outcome": {
        "text": "A publicação deve conter responsável e origem.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "exceptions": [],
      "note": "A declaração não estabelece exceções.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar as publicações da equipe, suas fontes e o registro de decisões.",
      "note": "Propósito extraído da concepção e da descrição do backlog.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "audience",
      "text": "Autores.",
      "note": "Público explicitamente declarado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano são princípios do projeto.",
      "note": "Esses princípios não definem etapas de aprovação ou permissões específicas.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de espaço de trabalho para organização de publicações de uma equipe.",
      "note": "Interpretação da declaração de domínio em conjunto com a concepção.",
      "context_indices": [
        0,
        7
      ]
    },
    {
      "subject": "capability",
      "text": "Registrar decisões relacionadas à organização das publicações.",
      "note": "Capacidade declarada em termos amplos, sem exigir um formato específico.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "Deve ser registrada a identidade do responsável.",
      "note": "Obrigação explícita cuja aplicabilidade não foi especificada. Sua preservação como restrição normativa não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é de US$ 0,00.",
      "note": "Limite informado pelo campo max_build_cost_usd.",
      "context_indices": [
        5
      ]
    }
  ],
  "issues": []
}
```

## Fontes literais

```json
[
  {
    "id": "atom-1",
    "source_ref": "input-1",
    "pointer": "/conception",
    "quote": "Uma equipe organiza publicações e suas fontes.",
    "kind": "conception",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-2",
    "source_ref": "input-2",
    "pointer": "/branding/audience/0",
    "quote": "autores",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-3",
    "source_ref": "input-2",
    "pointer": "/branding/principles/0",
    "quote": "rastreabilidade",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-4",
    "source_ref": "input-2",
    "pointer": "/branding/principles/1",
    "quote": "controle humano",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-5",
    "source_ref": "input-3",
    "pointer": "/constraints/business/0",
    "quote": "Registrar a identidade do responsável.",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-6",
    "source_ref": "input-3",
    "pointer": "/constraints/max_build_cost_usd",
    "quote": "0.0",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-7",
    "source_ref": "input-4",
    "pointer": "/backlog/0/description",
    "quote": "Organizar publicação da equipe e registrar decisões.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-8",
    "source_ref": "input-5",
    "pointer": "/backlog/0/acceptance_criteria/0",
    "quote": "Cada publicação da equipe deve conter responsável e origem.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-9",
    "source_ref": "input-6",
    "pointer": "/domain",
    "quote": "workspace-management",
    "kind": "domain-declaration",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-10",
    "source_ref": "input-7",
    "pointer": "/assets/0/path",
    "quote": "assets/brand-notes.md",
    "kind": "asset-metadata",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-11",
    "source_ref": "input-7",
    "pointer": "/assets/0/description",
    "quote": "Referência declarada; conteúdo não ingerido.",
    "kind": "asset-metadata",
    "content_trust": "untrusted-data"
  }
]
```

## Inventário de achados e componentes

```json
[
  {
    "id": "criterion-1",
    "kind": "rule",
    "text": "Cada publicação da equipe deve conter responsável e origem.",
    "condition": "Para cada publicação da equipe.",
    "outcome": "A publicação deve conter responsável e origem.",
    "exceptions": [],
    "impact": null,
    "rationale": "A declaração não estabelece exceções.",
    "source_atom_ids": [
      "atom-8"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-8"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-8"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "1728a0b4cf3c5ca19eee52621a3856b27c0a86c132771a4c9c0df48e8ef200c0"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar as publicações da equipe, suas fontes e o registro de decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Propósito extraído da concepção e da descrição do backlog.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "cbe4519ca2534ece1520836dc280173fcea033c4b9d00efaedf0783cdf441b90"
  },
  {
    "id": "context-2",
    "kind": "statement",
    "text": "Autores.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Público explicitamente declarado.",
    "source_atom_ids": [
      "atom-2"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "21dc6c05c2a088cab8529fa0e078ade2a529107573d3220261170e6468056dd9"
  },
  {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano são princípios do projeto.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Esses princípios não definem etapas de aprovação ou permissões específicas.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "b291995146062a63900c5c2fa37b1f8dd7a73e2d8068fe1aff1f67d125e8f6eb"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de espaço de trabalho para organização de publicações de uma equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Interpretação da declaração de domínio em conjunto com a concepção.",
    "source_atom_ids": [
      "atom-1",
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "b5ea9435fa14fc73ba11c14e8db33b2b2054ba6757cea2cdec5f10713030e6a8"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Registrar decisões relacionadas à organização das publicações.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidade declarada em termos amplos, sem exigir um formato específico.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "bf5af818cffd8c8a3fde5c0e1afa32aff779aa257e4cceee60d3e684c1952e2e"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "Deve ser registrada a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita cuja aplicabilidade não foi especificada. Sua preservação como restrição normativa não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "99a549948f1d1bd83dbec67c79c1250f81934a5ba1a9e4937c56105d52fbb29c"
  },
  {
    "id": "context-7",
    "kind": "statement",
    "text": "O custo máximo de construção é de US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite informado pelo campo max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "e34d269ee55f859b1ea602aaf69c5f761fe9c791fac4224ddfd579c8e980c5e6"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "8fb9315474f6ffb0bcc0a79d8ba08960da0d0acd814238d0137c7d5234223fc4",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "1728a0b4cf3c5ca19eee52621a3856b27c0a86c132771a4c9c0df48e8ef200c0",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige responsável e origem para cada publicação da equipe."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "cbe4519ca2534ece1520836dc280173fcea033c4b9d00efaedf0783cdf441b90",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem organizar publicações e fontes e registrar decisões."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "21dc6c05c2a088cab8529fa0e078ade2a529107573d3220261170e6468056dd9",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O público declarado é autores."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "b291995146062a63900c5c2fa37b1f8dd7a73e2d8068fe1aff1f67d125e8f6eb",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambos os princípios estão explicitamente declarados; não especificam permissões ou aprovação."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "b5ea9435fa14fc73ba11c14e8db33b2b2054ba6757cea2cdec5f10713030e6a8",
      "source_atom_ids": [
        "atom-1",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio workspace-management e a concepção sustentam a descrição contextual."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "bf5af818cffd8c8a3fde5c0e1afa32aff779aa257e4cceee60d3e684c1952e2e",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Registrar decisões aparece junto à organização da publicação da equipe."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "99a549948f1d1bd83dbec67c79c1250f81934a5ba1a9e4937c56105d52fbb29c",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A obrigação de registrar a identidade do responsável é explícita, mas sua aplicabilidade não está definida."
    },
    {
      "finding_id": "context-7",
      "finding_sha256": "e34d269ee55f859b1ea602aaf69c5f761fe9c791fac4224ddfd579c8e980c5e6",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd informa limite de 0.0 dólares."
    }
  ],
  "component_judgments": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "Cada publicação da equipe é o âmbito explicitamente declarado."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A fonte exige que a publicação contenha responsável e origem."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "A quais situações se aplica a obrigação de registrar a identidade do responsável?",
      "rationale": "A restrição preservada em context-6 não delimita sua aplicação; esclarecer esse âmbito altera a regra de registro exigida.",
      "source_atom_ids": [
        "atom-5"
      ],
      "impact": "rule"
    }
  ],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "88b9866f0e0b53ae15c7d6439e0c540ac09134f17f179c297c4dde265f0c01eb",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "context-4"
      ],
      "omission_ids": [],
      "note": "Concepção representada nos dois achados."
    },
    {
      "atom_id": "atom-2",
      "quote_sha256": "75f26d13ebd8877644c57a369ce71b82b639903217ed12ebe61beeffd8c11586",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público preservado."
    },
    {
      "atom_id": "atom-3",
      "quote_sha256": "e8a964e534bd9189a4c1ee68dc1e80429c5b14930ce7df548075257a8a8dccc7",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Princípio de rastreabilidade preservado."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "a6e3b461d6bc6975496196edb2b7d4ea96130a66c49e4e058c4d66078d23422f",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Controle humano preservado sem inferir autoridade de aprovação."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "missing",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Obrigação preservada separadamente; falta a pergunta material sobre sua aplicabilidade."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-7"
      ],
      "omission_ids": [],
      "note": "Limite de custo preservado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "context-5"
      ],
      "omission_ids": [],
      "note": "Organização e registro de decisões representados."
    },
    {
      "atom_id": "atom-9",
      "quote_sha256": "d8ec0dfaccceaea0a5f8ccf5a95f094560df5ea36683833d84877c601223e217",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Domínio representado."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "a79c1f7e236f6dadc2d66f9ab1ce333e7c271bfe617435c1f8e49ce579b92ef2",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Regra integralmente representada por condição e resultado."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
