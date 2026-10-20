# Revisão do candidato v3.3 — dev-new-domain

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
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "analysis_sha256": "a8fa5a8dd242658b384e0392466bed1f5bdc9505e78eaf8cefb8f460ce7b09e0",
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
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-new-domain/summary.json",
      "sha256": "b272425b065afbca4f785bc592d845e8e8b731592cff284ecc3eafa6a6601c84"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-new-domain/analysis.json",
      "sha256": "eafac4d053ef68e749b4a16e0cc4c9b67c9dc9190cf3cd8b385d0b54fe08796d"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-new-domain/assessment.json",
      "sha256": "1646befcf56ba70c221e4bd39995ff7b420da93b6dc30f0504911a695571fa1e"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-new-domain/advice.json",
      "sha256": "b0da1c979e5fca56dd840a9932f60f89d2b73866ee11ddd063f86f5b9d1057a7"
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
      "text": "Em quais situações deve ser registrada a identidade do responsável, e a quem se refere esse responsável?",
      "rationale": "A obrigação foi preservada, mas falta esclarecer seu alcance e sujeito para determinar quando e de quem exigir identidade.",
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
      "note": "Propósito declarado do projeto.",
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
      "note": "Os princípios orientam o projeto sem definir procedimentos adicionais de aprovação.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Experiências coletivas com lanternas sensoriais e organização de publicações da equipe.",
      "note": "Domínio inferido do propósito e da descrição do trabalho.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar a publicação da equipe e registrar decisões.",
      "note": "Capacidades declaradas; não foram especificados formatos de registro.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade desta obrigação não foi especificada. Sua preservação como restrição normativa não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite declarado pelo campo max_build_cost_usd.",
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
    "rationale": "Propósito declarado do projeto.",
    "source_atom_ids": [
      "atom-1"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "9eb70dfb695f39ef53048c4b77f488f67e98d5b5b71012f26c2ee081b3d94717"
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
    "rationale": "Os princípios orientam o projeto sem definir procedimentos adicionais de aprovação.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "f302dfaa88c917d2345766ba858fb41902783d7456445ef7becb71b4765302b6"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Experiências coletivas com lanternas sensoriais e organização de publicações da equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio inferido do propósito e da descrição do trabalho.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "c6b8dfe54b9b77a2f1800e0a7f3099b58d7301a5bac4aa7290d911ead78c8b3d"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Organizar a publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades declaradas; não foram especificados formatos de registro.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "49c2b29ad12ec44daa4941d5c76c847a342b94d8c75a4416098f7582e6406a79"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade desta obrigação não foi especificada. Sua preservação como restrição normativa não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "2ad45e0ead3ebaeb80f426a21e78b14f47fec1b6c413ede253c674a5c31e950b"
  },
  {
    "id": "context-7",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado pelo campo max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "0bdeb5f562dac3e671ecb75e10394e4772be624855720a315fbba9082f8a78a4"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "a8fa5a8dd242658b384e0392466bed1f5bdc9505e78eaf8cefb8f460ce7b09e0",
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
      "finding_sha256": "9eb70dfb695f39ef53048c4b77f488f67e98d5b5b71012f26c2ee081b3d94717",
      "source_atom_ids": [
        "atom-1"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Reproduz o propósito declarado na concepção."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo de público declara autores."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "f302dfaa88c917d2345766ba858fb41902783d7456445ef7becb71b4765302b6",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os campos de princípios declaram rastreabilidade e controle humano; não especificam aprovação."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "c6b8dfe54b9b77a2f1800e0a7f3099b58d7301a5bac4aa7290d911ead78c8b3d",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A concepção e a descrição sustentam os dois aspectos do domínio."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "49c2b29ad12ec44daa4941d5c76c847a342b94d8c75a4416098f7582e6406a79",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A descrição declara organizar publicação e registrar decisões."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "2ad45e0ead3ebaeb80f426a21e78b14f47fec1b6c413ede253c674a5c31e950b",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável, sem definir sua aplicabilidade ou identificar quem é responsável."
    },
    {
      "finding_id": "context-7",
      "finding_sha256": "0bdeb5f562dac3e671ecb75e10394e4772be624855720a315fbba9082f8a78a4",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd fixa o limite em zero."
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
      "note": "“Cada publicação da equipe” estabelece o alcance da condição."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "“Deve conter responsável e origem” estabelece a obrigação."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Em quais situações deve ser registrada a identidade do responsável, e a quem se refere esse responsável?",
      "rationale": "A obrigação foi preservada, mas falta esclarecer seu alcance e sujeito para determinar quando e de quem exigir identidade.",
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
        "context-1",
        "context-4"
      ],
      "omission_ids": [],
      "note": "Concepção representada como propósito e domínio."
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
      "note": "Controle humano representado sem inferir autoridade de aprovação."
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
      "note": "Restrição preservada separadamente; falta a pergunta material sobre alcance e sujeito."
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
        "context-4",
        "context-5"
      ],
      "omission_ids": [],
      "note": "Organização de publicação e registro de decisões representados."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "a79c1f7e236f6dadc2d66f9ab1ce333e7c271bfe617435c1f8e49ce579b92ef2",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Obrigação por publicação representada integralmente."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
