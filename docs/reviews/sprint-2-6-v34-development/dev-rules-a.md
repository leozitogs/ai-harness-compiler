# Revisão do candidato v3.4 — dev-rules-a

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-rules-a",
  "baseline_selected_status": "pass",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "d4dca46e801c7f9f89d799226af6929fd582d847c00ec8500378b6b5c3435341",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "previous_round_status": "pass",
  "previous_round_analysis_sha256": "0322100803ba35de424ff2d70921a770eddbe317b66c61c86f10a6efbd2bbc34",
  "identical_to_previous_round": false,
  "analysis_sha256": "e6cae0c80e4a70606117e9a9b60f875539b1ed3593e7fc7f188ca67be8a25143",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-rules-a.json",
      "sha256": "5c22bb8748b1badaca5f7e2ba66d5ef628fc95128bdb5479617a7f5094220063"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-a/summary.json",
      "sha256": "216653f039f9b7c961dd7894965f481cc7b696a9ee1e72cf8048aabb0c768acb"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-a/analysis.json",
      "sha256": "bf554bece353c2ec7729c64fda5fa55f8fe1c18ed03f1dfac52a26311466bb99"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-a/assessment.json",
      "sha256": "c2cd9895aba1a5b2f38471eb8d59f76b5c1c3f79c918ebf47fad316d60de4d3a"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-a/advice.json",
      "sha256": "c73fb2a80868387ffb3a97f4cdcde861f56dd4eb1e90546058f50197bf03a4c4"
    }
  ],
  "findings": 8,
  "components": 2,
  "questions": [],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "question-1",
      "kind": "question",
      "text": "Em quais operações deve ser registrada a identidade e quem é o responsável cujo registro é exigido?",
      "rationale": "A obrigação foi preservada, mas falta definir seu sujeito e sua aplicabilidade; isso altera a regra de registro sem autorizar equiparação ao aprovador.",
      "source_atom_ids": [
        "atom-5"
      ],
      "impact": "rule"
    },
    {
      "id": "question-2",
      "kind": "question",
      "text": "Quem é o responsável designado cuja aprovação permite satisfazer a exigência de liberação?",
      "rationale": "A fonte exige aprovação de um papel específico, mas não determina quem o ocupa ou como reconhecê-lo; a resposta altera quais aprovações são válidas.",
      "source_atom_ids": [
        "atom-8"
      ],
      "impact": "authorization"
    }
  ],
  "advisory_negative_components": []
}
```

## Input completo

```json
{
  "schema_version": "ProjectInput/v1",
  "id": "dev-rules-a",
  "name": "Fixture dev rules-a",
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
        "Liberar publicação da equipe exige aprovação do responsável designado."
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
    "id": "dev-rules-a",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "Liberar publicação da equipe exige aprovação do responsável designado.",
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
        "text": "Para liberar publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "outcome": {
        "text": "É necessária a aprovação do responsável designado.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "exceptions": [],
      "note": "A aprovação é uma condição necessária; o texto não declara que ela, isoladamente, seja suficiente para liberar a publicação.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar publicações da equipe e suas fontes, registrando decisões.",
      "note": "Finalidade declarada na concepção e na descrição do backlog.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "audience",
      "text": "Autores.",
      "note": "Público explicitamente informado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano.",
      "note": "Princípios declarados para orientar o projeto.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de espaços de trabalho, com organização de publicações e fontes.",
      "note": "Interpretação da declaração workspace-management à luz da concepção.",
      "context_indices": [
        0,
        7
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar publicações e fontes e registrar decisões da equipe.",
      "note": "Capacidades amplas; os formatos dos registros não foram especificados.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade não foi especificada. A obrigação permanece explícita, sem uma política executável de aplicabilidade e sem equiparar esse responsável ao responsável designado para aprovação.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite declarado no campo max_build_cost_usd.",
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
    "quote": "Liberar publicação da equipe exige aprovação do responsável designado.",
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
  }
]
```

## Inventário de achados e componentes

```json
[
  {
    "id": "criterion-1",
    "kind": "rule",
    "text": "Liberar publicação da equipe exige aprovação do responsável designado.",
    "condition": "Para liberar publicação da equipe.",
    "outcome": "É necessária a aprovação do responsável designado.",
    "exceptions": [],
    "impact": null,
    "rationale": "A aprovação é uma condição necessária; o texto não declara que ela, isoladamente, seja suficiente para liberar a publicação.",
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
    "sha256": "8c984d76acee89581e11b7a0fc904d642ceb37c0a1851af33efda010f5b315bb"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar publicações da equipe e suas fontes, registrando decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Finalidade declarada na concepção e na descrição do backlog.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "36ba56209547c89ade469f5f5f057e2d87c98f66a38b695bb8518b11e89edc97"
  },
  {
    "id": "context-2",
    "kind": "statement",
    "text": "Autores.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Público explicitamente informado.",
    "source_atom_ids": [
      "atom-2"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "d59bb363e99ce9e22455c9c027a3edeb79dd5ac3603853380ee2aa3fa97fa1f4"
  },
  {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Princípios declarados para orientar o projeto.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "99f9e7b91f43bfee9ea5de9d19676e55ab7742a6ac72f07fbb1a041b28f03deb"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de espaços de trabalho, com organização de publicações e fontes.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Interpretação da declaração workspace-management à luz da concepção.",
    "source_atom_ids": [
      "atom-1",
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "c66920edb6532a7ce8b49404d9a47e8ba58aa2ac79fe248422c248be33067014"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Organizar publicações e fontes e registrar decisões da equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades amplas; os formatos dos registros não foram especificados.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "7c2fb45a91f1585664c953f49c81d1e66416be8caf515c4ef921cc274f9592b6"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade não foi especificada. A obrigação permanece explícita, sem uma política executável de aplicabilidade e sem equiparar esse responsável ao responsável designado para aprovação.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "a9628fdbb34e51ca9fb97f619d32cd14cbf241fb4760b95b9759a0535b97b516"
  },
  {
    "id": "context-7",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado no campo max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "8d7404bee925e16f8eac6f16e57a36dcd43cab69512890354ef2692eb1a24afd"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "e6cae0c80e4a70606117e9a9b60f875539b1ed3593e7fc7f188ca67be8a25143",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "8c984d76acee89581e11b7a0fc904d642ceb37c0a1851af33efda010f5b315bb",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige aprovação do responsável designado para liberar publicação, sem afirmar suficiência."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "36ba56209547c89ade469f5f5f057e2d87c98f66a38b695bb8518b11e89edc97",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram organização de publicações e fontes e registro de decisões."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "d59bb363e99ce9e22455c9c027a3edeb79dd5ac3603853380ee2aa3fa97fa1f4",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O público declarado é autores."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "99f9e7b91f43bfee9ea5de9d19676e55ab7742a6ac72f07fbb1a041b28f03deb",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambos os princípios estão expressos nas fontes."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "c66920edb6532a7ce8b49404d9a47e8ba58aa2ac79fe248422c248be33067014",
      "source_atom_ids": [
        "atom-1",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio declarado e a concepção sustentam essa descrição."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "7c2fb45a91f1585664c953f49c81d1e66416be8caf515c4ef921cc274f9592b6",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As capacidades descritas constam das duas fontes."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "a9628fdbb34e51ca9fb97f619d32cd14cbf241fb4760b95b9759a0535b97b516",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável; não identifica esse papel nem estabelece sua aplicabilidade ou equivalência ao aprovador."
    },
    {
      "finding_id": "context-7",
      "finding_sha256": "8d7404bee925e16f8eac6f16e57a36dcd43cab69512890354ef2692eb1a24afd",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd declara limite de 0.0."
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
      "note": "A fonte situa a exigência na liberação da publicação da equipe."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A aprovação do responsável designado é expressamente necessária."
    }
  ],
  "omissions": [
    {
      "id": "question-1",
      "kind": "question",
      "text": "Em quais operações deve ser registrada a identidade e quem é o responsável cujo registro é exigido?",
      "rationale": "A obrigação foi preservada, mas falta definir seu sujeito e sua aplicabilidade; isso altera a regra de registro sem autorizar equiparação ao aprovador.",
      "source_atom_ids": [
        "atom-5"
      ],
      "impact": "rule"
    },
    {
      "id": "question-2",
      "kind": "question",
      "text": "Quem é o responsável designado cuja aprovação permite satisfazer a exigência de liberação?",
      "rationale": "A fonte exige aprovação de um papel específico, mas não determina quem o ocupa ou como reconhecê-lo; a resposta altera quais aprovações são válidas.",
      "source_atom_ids": [
        "atom-8"
      ],
      "impact": "authorization"
    }
  ],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "88b9866f0e0b53ae15c7d6439e0c540ac09134f17f179c297c4dde265f0c01eb",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "context-4",
        "context-5"
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
      "note": "Princípio representado."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "a6e3b461d6bc6975496196edb2b7d4ea96130a66c49e4e058c4d66078d23422f",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Princípio representado."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "missing",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [
        "question-1"
      ],
      "note": "Obrigação preservada separadamente da aprovação; falta esclarecer sujeito e aplicabilidade."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-7"
      ],
      "omission_ids": [],
      "note": "Limite de custo representado."
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
      "quote_sha256": "1d64d3523733ce851e3da43cce5b1d659b91e31ad337dd6cd2d26f46483a4650",
      "disposition": "missing",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [
        "question-2"
      ],
      "note": "Exigência representada; falta identificar o papel autorizado a aprovar."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
