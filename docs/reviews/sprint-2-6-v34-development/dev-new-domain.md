# Revisão do candidato v3.4 — dev-new-domain

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-new-domain",
  "baseline_selected_status": "pass",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "8baff4b157478c6a6bc91fca505875990ff3e3dddb73350149faea240a897a2a",
  "new_generation": "valid",
  "new_audit": "error",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "previous_round_status": "pass",
  "previous_round_analysis_sha256": "a8fa5a8dd242658b384e0392466bed1f5bdc9505e78eaf8cefb8f460ce7b09e0",
  "identical_to_previous_round": false,
  "analysis_sha256": "fc4acfb7442988d28fa2af9fc57325b0a42f0532c34c643cd2ddeca174b3011c",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-new-domain.json",
      "sha256": "03d5682c906e6b053951195ef3c97d81453306cf51584f861e06e9d7dff0b16c"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/summary.json",
      "sha256": "7be38c924fbeff365bf290b206c92d885e74d398610c38d222dbf9136b7dd605"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/analysis.json",
      "sha256": "0e11576c34122bae66466f8ca03016cf059f27ec27c856550062d53bff467789"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/assessment.json",
      "sha256": "0076c6b3157ef1e6e9cf403c3a3ecdd5d98c42e2ef225083ba0d8d3ed4ac2675"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/audit-response.txt",
      "sha256": "bbedde59bfd4eb728f6b18e142427513e02f750a4c034ff2922f6d1384fa3da5"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/audit-diagnostic.json",
      "sha256": "6721306627b5aa6026775e988acc6985c31434df26f5e67c97d96d69c1d07b4d"
    }
  ],
  "findings": 7,
  "components": 2,
  "questions": [],
  "guards": [],
  "advisory_omissions": null,
  "advisory_negative_components": null
}
```

## Input completo

```json
{
  "schema_version": "ProjectInput/v1",
  "id": "dev-new-domain",
  "name": "Fixture dev new-domain",
  "conception": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
  "domain": null,
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
  "assets": [],
  "evidence_pack": null,
  "domain_profile": null
}
```

## Expectativas e rubrica aprovadas

```json
{
  "case": {
    "schema_version": "AssessmentCase/v2",
    "id": "dev-new-domain",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "publication-origin",
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
      "note": "Obrigação aplicável a cada publicação da equipe.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
      "note": "Finalidade declarada do projeto.",
      "context_indices": [
        0
      ]
    },
    {
      "subject": "audience",
      "text": "Autores.",
      "note": "Público declarado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano são princípios do projeto.",
      "note": "Não especificam fluxos de aprovação ou permissões.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar a publicação da equipe e registrar decisões.",
      "note": "Capacidades de apoio declaradas.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "Registrar a identidade do responsável.",
      "note": "Obrigação explícita cuja aplicabilidade não foi especificada. Sua representação como contexto normativo não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite declarado em /constraints/max_build_cost_usd.",
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
    "quote": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
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
    "rationale": "Obrigação aplicável a cada publicação da equipe.",
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
    "sha256": "c79233c9c2342298205e15e5773ad28c4acc3876d5105130e9bf9334c6896ada"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Finalidade declarada do projeto.",
    "source_atom_ids": [
      "atom-1"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "76cf654206351f3d9169f62e3f137904a1dd12022ba81507b754e7de2b00640b"
  },
  {
    "id": "context-2",
    "kind": "statement",
    "text": "Autores.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Público declarado.",
    "source_atom_ids": [
      "atom-2"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d"
  },
  {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano são princípios do projeto.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Não especificam fluxos de aprovação ou permissões.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "f485b96e0a2eeb415a8554672ce20d83d20155b8d4e78adecf76193f90f382c9"
  },
  {
    "id": "context-4",
    "kind": "statement",
    "text": "Organizar a publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades de apoio declaradas.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "46de9c728fd7bb9a3d5c5c1c5c2e81ec7ae825fb5bbe4d7a3593f94d0502d532"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita cuja aplicabilidade não foi especificada. Sua representação como contexto normativo não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "ba094e70a55cc318aec56906b2493d320e0f4386d046ab5da6f2cc86e30ead51"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado em /constraints/max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "a418a027eee6345b2f61aaaafe7093ea6db863635e343ea4d74eb437d1a966d7"
  }
]
```

## Parecer consultivo

```json
{
  "status": "error",
  "raw_proposal": {
    "schema_version": "SemanticVerifierProposal/v4",
    "analysis_sha256": "fc4acfb7442988d28fa2af9fc57325b0a42f0532c34c643cd2ddeca174b3011c",
    "findings": [
      {
        "finding_id": "criterion-1",
        "finding_sha256": "c79233c9c2342298205e15e5773ad28c4acc3876d5105130e9bf9334c6896ada",
        "source_atom_ids": [
          "atom-8"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "A fonte exige responsável e origem em cada publicação da equipe."
      },
      {
        "finding_id": "context-1",
        "finding_sha256": "76cf654206351f3d9169f62e3f137904a1dd12022ba81507b754e7de2b00640b",
        "source_atom_ids": [
          "atom-1"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "Reproduz a finalidade declarada na concepção."
      },
      {
        "finding_id": "context-2",
        "finding_sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d",
        "source_atom_ids": [
          "atom-2"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "O público informado é autores."
      },
      {
        "finding_id": "context-3",
        "finding_sha256": "f485b96e0a2eeb415a8554672ce20d83d20155b8d4e78adecf76193f90f382c9",
        "source_atom_ids": [
          "atom-3",
          "atom-4"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "Os dois princípios constam das fontes; não definem aprovação ou autorização."
      },
      {
        "finding_id": "context-4",
        "finding_sha256": "46de9c728fd7bb9a3d5c5c1c5c2c81ec7ae825fb5bbe4d7a3593f94d0502d532",
        "source_atom_ids": [
          "atom-7"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "A descrição declara organização da publicação e registro de decisões."
      },
      {
        "finding_id": "context-5",
        "finding_sha256": "ba094e70a55cc318aec56906b2493d320e0f4386d046ab5da6f2cc86e30ead51",
        "source_atom_ids": [
          "atom-5"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "A obrigação de registrar a identidade é explícita; sua aplicabilidade permanece indefinida."
      },
      {
        "finding_id": "context-6",
        "finding_sha256": "a418a027eee6345b2f61aaaafe7093ea6db863635e343ea4d74eb437d1a966d7",
        "source_atom_ids": [
          "atom-6"
        ],
        "support": "supports",
        "materiality": "not-applicable",
        "note": "O valor zero e o caminho max_build_cost_usd sustentam o limite declarado."
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
        "note": "Cada publicação da equipe é o âmbito explicitamente indicado."
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
        "text": "A quais ações ou registros se aplica a obrigação de registrar a identidade do responsável?",
        "rationale": "A restrição exige o registro, mas não delimita sua aplicação; essa resposta altera o âmbito da regra.",
        "source_atom_ids": [
          "atom-5"
        ],
        "impact": "rule"
      }
    ],
    "source_coverage": [
      {
        "atom_id": "atom-1",
        "quote_sha256": "6a4cc099f7c4beb8d98900b9d05f869383bb403a8803126d3f55c73886e0e7ce",
        "disposition": "represented",
        "finding_ids": [
          "context-1"
        ],
        "omission_ids": [],
        "note": "Concepção representada."
      },
      {
        "atom_id": "atom-2",
        "quote_sha256": "75f26d13ebd8877644c57a369ce71b82b639903217ed12ebe61beeffd8c11586",
        "disposition": "represented",
        "finding_ids": [
          "context-2"
        ],
        "omission_ids": [],
        "note": "Público representado."
      },
      {
        "atom_id": "atom-3",
        "quote_sha256": "e8a964e534bd9189a4c1ee68dc1e80429c5b14930ce7df548075257a8a8dccc7",
        "disposition": "represented",
        "finding_ids": [
          "context-3"
        ],
        "omission_ids": [],
        "note": "Princípio de rastreabilidade representado."
      },
      {
        "atom_id": "atom-4",
        "quote_sha256": "a6e3b461d6bc6975496196edb2b7d4ea96130a66c49e4e058c4d66078d23422f",
        "disposition": "represented",
        "finding_ids": [
          "context-3"
        ],
        "omission_ids": [],
        "note": "Princípio de controle humano representado, sem autorização inferida."
      },
      {
        "atom_id": "atom-5",
        "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
        "disposition": "missing",
        "finding_ids": [
          "context-5"
        ],
        "omission_ids": [
          "omission-1"
        ],
        "note": "Obrigação representada; falta a questão material sobre sua aplicabilidade."
      },
      {
        "atom_id": "atom-6",
        "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
        "disposition": "represented",
        "finding_ids": [
          "context-6"
        ],
        "omission_ids": [],
        "note": "Limite de custo representado."
      },
      {
        "atom_id": "atom-7",
        "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
        "disposition": "represented",
        "finding_ids": [
          "context-4"
        ],
        "omission_ids": [],
        "note": "Ambas as capacidades declaradas estão representadas."
      },
      {
        "atom_id": "atom-8",
        "quote_sha256": "a79c1f7e236f6dadc2d66f9ab1ce333e7c271bfe617435c1f8e49ce579b92ef2",
        "disposition": "represented",
        "finding_ids": [
          "criterion-1"
        ],
        "omission_ids": [],
        "note": "Obrigação por publicação representada."
      }
    ]
  },
  "diagnostic": {
    "binding_valid": false,
    "case": "dev-new-domain",
    "format": "offline-audit-diagnostic/v1",
    "mismatches": [
      {
        "expected_sha256": "46de9c728fd7bb9a3d5c5c1c5c2e81ec7ae825fb5bbe4d7a3593f94d0502d532",
        "expected_sources": [
          "atom-7"
        ],
        "finding_id": "context-4",
        "observed_sha256": "46de9c728fd7bb9a3d5c5c1c5c2c81ec7ae825fb5bbe4d7a3593f94d0502d532",
        "observed_sources": [
          "atom-7"
        ]
      }
    ],
    "proposal_parses": true,
    "reason": "Verifier finding digest or exact source binding differs",
    "repairs": 0,
    "retries": 0,
    "scope": "Saved final response only; no provider call or rewriting",
    "semantic_approval": false
  }
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
