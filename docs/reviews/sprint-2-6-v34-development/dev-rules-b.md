# Revisão do candidato v3.4 — dev-rules-b

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-rules-b",
  "baseline_selected_status": "fail",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "37259cfadefec1d810777fb46d24278122889ce8e2703457e2518d39ffee6231",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "previous_round_status": "pass",
  "previous_round_analysis_sha256": "7e5bf07604bd4d6478a4f66bc4126417523c530e47337f67ba26f2beedcba989",
  "identical_to_previous_round": false,
  "analysis_sha256": "b2293470cbd7d736a96b0bb9cc815cbdae7f5d76b490664ca38bd91810d388ad",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-rules-b.json",
      "sha256": "9e516037eefd452f56323845d4aa5adc613a713d34b77da788c5629eaf131fa0"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-b/summary.json",
      "sha256": "f5e825aa88903e16752683998a14328acbffc6c941f6e2fcb0ce3fdc9ff6e029"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-b/analysis.json",
      "sha256": "1c018a151eafdecad3d344c07c8ec9c30a07d46cf2e0ed45a77c5c949b914949"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-b/assessment.json",
      "sha256": "4879e8befaa387ef114ecac2c70e92bac66f1b140dd17b92b729b7a667bf370a"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-rules-b/advice.json",
      "sha256": "9d8daf7885863ad1076b0c2b40ae03772c8c2ccac0b8bb25ac1d2708f48a3722"
    }
  ],
  "findings": 7,
  "components": 2,
  "questions": [],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "A quais operações se aplica o registro obrigatório de identidade e quem é o responsável cuja identidade deve ser registrada?",
      "rationale": "A restrição não define seu alcance nem o papel responsável. A resposta altera a regra de registro; não se pode presumir que responsável seja autor ou executor autenticado.",
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
  "id": "dev-rules-b",
  "name": "Fixture dev rules-b",
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
        "O autor pode liberar publicação da equipe sem aprovação de terceiros."
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
    "id": "dev-rules-b",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
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
        "text": "O autor pretende liberar uma publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "outcome": {
        "text": "O autor pode liberar a publicação sem aprovação de terceiros.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "exceptions": [],
      "note": "A autorização não depende de aprovação adicional.",
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
      "note": "Público explicitamente declarado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano orientam o projeto.",
      "note": "Esses princípios não estabelecem exigência de aprovação de terceiros.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de workspace para organização de publicações e fontes de uma equipe.",
      "note": "Interpretação da declaração de domínio à luz da concepção.",
      "context_indices": [
        0,
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade não foi especificada: a declaração não define operação ou condição para esse registro. A obrigação permanece explícita, sem fornecer uma política executável de aplicabilidade nem acrescentar aprovação à liberação de publicações.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de build é US$ 0,00.",
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
    "quote": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
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
    "text": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
    "condition": "O autor pretende liberar uma publicação da equipe.",
    "outcome": "O autor pode liberar a publicação sem aprovação de terceiros.",
    "exceptions": [],
    "impact": null,
    "rationale": "A autorização não depende de aprovação adicional.",
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
    "sha256": "ad73cb487266c82f89325a9ef8e31de9ca4a8c760d15c10b1b881c4b9268fec7"
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
    "text": "Rastreabilidade e controle humano orientam o projeto.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Esses princípios não estabelecem exigência de aprovação de terceiros.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "ccf5162a54c23ace56e810a6cdb087028e7970fc64b623a950bb147b0d7c5b05"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de workspace para organização de publicações e fontes de uma equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Interpretação da declaração de domínio à luz da concepção.",
    "source_atom_ids": [
      "atom-1",
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "c21cbd018cbf8375f19b8fdb5bd66ab790b341f01d5e7a7e5a9d0b7e4105c3b4"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade não foi especificada: a declaração não define operação ou condição para esse registro. A obrigação permanece explícita, sem fornecer uma política executável de aplicabilidade nem acrescentar aprovação à liberação de publicações.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "208f61fa8b39ed14fc4c25d9a6bfe8630399c8ae7686c1ebcf5f58049041d466"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de build é US$ 0,00.",
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
    "sha256": "1777e0fab8c4a8cb9b37467b782e63b7fc29125f290662ee5b1375004038f5b2"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "b2293470cbd7d736a96b0bb9cc815cbdae7f5d76b490664ca38bd91810d388ad",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "ad73cb487266c82f89325a9ef8e31de9ca4a8c760d15c10b1b881c4b9268fec7",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte autoriza expressamente o autor a liberar publicação da equipe sem aprovação de terceiros."
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
      "finding_sha256": "ccf5162a54c23ace56e810a6cdb087028e7970fc64b623a950bb147b0d7c5b05",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Rastreabilidade e controle humano são princípios explícitos; não especificam aprovação de terceiros."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "c21cbd018cbf8375f19b8fdb5bd66ab790b341f01d5e7a7e5a9d0b7e4105c3b4",
      "source_atom_ids": [
        "atom-1",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio workspace-management é contextualizado pela organização de publicações e fontes da equipe."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "208f61fa8b39ed14fc4c25d9a6bfe8630399c8ae7686c1ebcf5f58049041d466",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável, mas não define aplicabilidade nem identifica esse responsável. Permanece separada da permissão de publicação."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "1777e0fab8c4a8cb9b37467b782e63b7fc29125f290662ee5b1375004038f5b2",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd contém 0.0, sustentando o limite declarado."
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
      "note": "A permissão trata do autor que pretende liberar publicação da equipe."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A liberação sem aprovação de terceiros é expressamente permitida."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "A quais operações se aplica o registro obrigatório de identidade e quem é o responsável cuja identidade deve ser registrada?",
      "rationale": "A restrição não define seu alcance nem o papel responsável. A resposta altera a regra de registro; não se pode presumir que responsável seja autor ou executor autenticado.",
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
      "note": "Concepção representada na finalidade e no domínio."
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
      "note": "Princípio de controle humano representado."
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
      "note": "Obrigação representada; falta a pergunta material sobre alcance e identidade responsável."
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
        "context-1"
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
      "quote_sha256": "66d4ab88ea3d6f5d267015ed9c60dbb7fcc14ebdb910f90b34b27579c499e240",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Permissão explícita representada; não conflita com a obrigação separada de registro."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
