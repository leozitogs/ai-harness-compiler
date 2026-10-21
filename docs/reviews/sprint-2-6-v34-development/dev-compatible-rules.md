# Revisão do candidato v3.4 — dev-compatible-rules

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-compatible-rules",
  "baseline_selected_status": "pass",
  "baseline_original_generation": "error",
  "baseline_selected_attempt": "schema-v31-recovery",
  "baseline_analysis_sha256": "09f6148f4cf0303325d2c3380e32f2735a13f543797df23da3b0ca9b4e956581",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "previous_round_status": "pass",
  "previous_round_analysis_sha256": "1cc497e0e8831edd2b1e1baed4313630a7a7345ebb23232555e09a0ac3bc5c40",
  "identical_to_previous_round": false,
  "analysis_sha256": "f62f9560aa2ecdebc90482158164890665a6a9d861501dc3b6fecd86b40ae5f8",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-compatible-rules.json",
      "sha256": "fc8a20bcd49950df782e5fc0e7ef39aea912e0b656b0198e24bfd546d7e96622"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-compatible-rules/summary.json",
      "sha256": "2b0a60cedb279159b3c1b6a9976cb135a8f5fc4a7911eafc78fad0938ca03f39"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-compatible-rules/analysis.json",
      "sha256": "3e73144158b221ec30ab8bdb3d9527cb1c4bf1cccfe135418db9ec932370ee2e"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-compatible-rules/assessment.json",
      "sha256": "c00999b97ee65b27bc81280a245c621692d82859ac6c42721df09ece69e71c38"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-compatible-rules/advice.json",
      "sha256": "ad9af20d9a4c91d8a712fa40316c2f3b51cc47116a4613c5671b360e9391ae9d"
    }
  ],
  "findings": 16,
  "components": 10,
  "questions": [],
  "guards": [
    {
      "id": "guard-human-review",
      "condition": "Antes de uma publicação.",
      "outcome": "Exigir revisão humana prévia.",
      "sources": [
        "atom-13"
      ]
    }
  ],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Como se determina o educador responsável autorizado a visualizar cada material?",
      "rationale": "A exclusividade está definida, mas falta o critério que vincula uma pessoa ao papel responsável; isso altera quem recebe acesso.",
      "source_atom_ids": [
        "atom-17"
      ],
      "impact": "authorization"
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "Qual educador pode fornecer a revisão e aprovação exigidas para uma publicação?",
      "rationale": "A fonte exige aprovação do educador sem identificar o vínculo que habilita essa pessoa a aprovar a publicação.",
      "source_atom_ids": [
        "atom-20"
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
  "id": "learning-studio",
  "name": "Learning Studio",
  "conception": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
  "domain": "education",
  "branding": {
    "audience": [
      "educadores",
      "coordenadores pedagógicos"
    ],
    "tone": [
      "claro",
      "acolhedor",
      "preciso"
    ],
    "principles": [
      "fontes verificáveis",
      "controle do educador"
    ],
    "visual_constraints": [
      "interface acessível"
    ]
  },
  "backlog": [
    {
      "id": "material-library",
      "title": "Biblioteca de materiais",
      "description": "Permitir que o educador catalogue materiais e suas fontes.",
      "acceptance_criteria": [
        "Cada material tem título, autor e referência de origem.",
        "Materiais só são visíveis ao educador responsável."
      ],
      "depends_on": [],
      "inputs": [
        "material",
        "metadados de origem"
      ],
      "outputs": [
        "material catalogado"
      ],
      "data_owner": "educador",
      "side_effects": [
        "gravação na biblioteca"
      ],
      "risk": "medium",
      "implementation": "deterministic"
    },
    {
      "id": "lesson-draft",
      "title": "Rascunho de aula baseado em fontes",
      "description": "Preparar um rascunho de aula usando os materiais selecionados.",
      "acceptance_criteria": [
        "As afirmações do rascunho referenciam os materiais utilizados.",
        "A publicação exige revisão e aprovação do educador."
      ],
      "depends_on": [
        "material-library"
      ],
      "inputs": [
        "materiais selecionados",
        "objetivos de aprendizagem"
      ],
      "outputs": [
        "rascunho com referências"
      ],
      "data_owner": "educador",
      "side_effects": [],
      "risk": "medium",
      "implementation": "rag"
    }
  ],
  "constraints": {
    "technical": [
      "Python 3.12 ou superior",
      "contratos versionados"
    ],
    "security": [
      "não expor dados pessoais em traces"
    ],
    "business": [
      "revisão humana antes de publicação"
    ],
    "max_build_cost_usd": 0.0
  },
  "assets": [
    {
      "path": "assets/brand-notes.md",
      "description": "Referência visual e verbal; conteúdo não ingerido no MVP."
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
    "id": "dev-compatible-rules",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "Cada material tem título, autor e referência de origem.",
        "disposition": "rule"
      },
      {
        "id": "required-2",
        "source_pointer": "/backlog/0/acceptance_criteria/1",
        "quote": "Materiais só são visíveis ao educador responsável.",
        "disposition": "rule"
      },
      {
        "id": "required-3",
        "source_pointer": "/backlog/1/acceptance_criteria/0",
        "quote": "As afirmações do rascunho referenciam os materiais utilizados.",
        "disposition": "rule"
      },
      {
        "id": "required-4",
        "source_pointer": "/backlog/1/acceptance_criteria/1",
        "quote": "A publicação exige revisão e aprovação do educador.",
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
      "source_atom_id": "atom-16",
      "kind": "business-rule",
      "condition": {
        "text": "Para cada material catalogado.",
        "source_atom_ids": [
          "atom-16"
        ]
      },
      "outcome": {
        "text": "O material deve ter título, autor e referência de origem.",
        "source_atom_ids": [
          "atom-16"
        ]
      },
      "exceptions": [],
      "note": "Obrigação de conteúdo para todos os materiais.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-17",
      "kind": "business-rule",
      "condition": {
        "text": "Na visualização de um material.",
        "source_atom_ids": [
          "atom-17"
        ]
      },
      "outcome": {
        "text": "O material só pode ser visível ao educador responsável.",
        "source_atom_ids": [
          "atom-17"
        ]
      },
      "exceptions": [],
      "note": "A presença de coordenadores pedagógicos no público não lhes concede acesso aos materiais.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-19",
      "kind": "business-rule",
      "condition": {
        "text": "Para cada afirmação do rascunho.",
        "source_atom_ids": [
          "atom-19"
        ]
      },
      "outcome": {
        "text": "A afirmação deve referenciar os materiais utilizados.",
        "source_atom_ids": [
          "atom-19"
        ]
      },
      "exceptions": [],
      "note": "Preserva a rastreabilidade das afirmações às fontes utilizadas.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-20",
      "kind": "business-rule",
      "condition": {
        "text": "Para publicar.",
        "source_atom_ids": [
          "atom-20"
        ]
      },
      "outcome": {
        "text": "É necessário haver revisão e aprovação do educador.",
        "source_atom_ids": [
          "atom-20"
        ]
      },
      "exceptions": [],
      "note": "Revisão e aprovação são requisitos necessários; a declaração não concede autorização suficiente por si só.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [
    {
      "id": "guard-human-review",
      "condition": {
        "text": "Antes de uma publicação.",
        "source_atom_ids": [
          "atom-13"
        ]
      },
      "effect": {
        "text": "Exigir revisão humana prévia.",
        "source_atom_ids": [
          "atom-13"
        ]
      },
      "target_scope": "project",
      "target_criterion_atom_ids": [],
      "note": "Restrição geral de publicação, também expressa na concepção; não substitui a aprovação do educador exigida pelo critério."
    }
  ],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar materiais e preparar aulas baseadas em fontes, com revisão humana antes da publicação.",
      "note": "Propósito declarado da plataforma.",
      "context_indices": [
        0
      ]
    },
    {
      "subject": "audience",
      "text": "Educadores e coordenadores pedagógicos.",
      "note": "Públicos declarados; não estabelece equivalência entre seus papéis ou permissões.",
      "context_indices": [
        1,
        2
      ]
    },
    {
      "subject": "tone",
      "text": "Claro, acolhedor e preciso.",
      "note": "Orientações de comunicação.",
      "context_indices": [
        3,
        4,
        5
      ]
    },
    {
      "subject": "positioning",
      "text": "Fontes verificáveis e controle do educador.",
      "note": "Princípios declarados do produto.",
      "context_indices": [
        6,
        7
      ]
    },
    {
      "subject": "domain",
      "text": "Educação.",
      "note": "Domínio explicitamente declarado.",
      "context_indices": [
        16
      ]
    },
    {
      "subject": "capability",
      "text": "Permitir ao educador catalogar materiais e suas fontes e preparar um rascunho de aula usando materiais selecionados.",
      "note": "Capacidades de apoio aos critérios.",
      "context_indices": [
        14,
        15
      ]
    },
    {
      "subject": "constraint",
      "text": "A interface deve ser acessível.",
      "note": "Obrigação explícita sem condição de aplicabilidade especificada; este registro não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        8
      ]
    },
    {
      "subject": "constraint",
      "text": "Usar Python 3.12 ou superior.",
      "note": "Restrição técnica explícita sem condição de aplicabilidade especificada.",
      "context_indices": [
        9
      ]
    },
    {
      "subject": "constraint",
      "text": "Os contratos devem ser versionados.",
      "note": "Obrigação explícita sem condição de aplicabilidade especificada; o mecanismo de versionamento não foi definido.",
      "context_indices": [
        10
      ]
    },
    {
      "subject": "constraint",
      "text": "Não expor dados pessoais em traces.",
      "note": "Proibição explícita sem gatilho de aplicabilidade especificado; permanece uma obrigação normativa.",
      "context_indices": [
        11
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite declarado em max_build_cost_usd, sem condição de aplicabilidade especificada.",
      "context_indices": [
        13
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
    "quote": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
    "kind": "conception",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-2",
    "source_ref": "input-2",
    "pointer": "/branding/audience/0",
    "quote": "educadores",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-3",
    "source_ref": "input-2",
    "pointer": "/branding/audience/1",
    "quote": "coordenadores pedagógicos",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-4",
    "source_ref": "input-2",
    "pointer": "/branding/tone/0",
    "quote": "claro",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-5",
    "source_ref": "input-2",
    "pointer": "/branding/tone/1",
    "quote": "acolhedor",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-6",
    "source_ref": "input-2",
    "pointer": "/branding/tone/2",
    "quote": "preciso",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-7",
    "source_ref": "input-2",
    "pointer": "/branding/principles/0",
    "quote": "fontes verificáveis",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-8",
    "source_ref": "input-2",
    "pointer": "/branding/principles/1",
    "quote": "controle do educador",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-9",
    "source_ref": "input-2",
    "pointer": "/branding/visual_constraints/0",
    "quote": "interface acessível",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-10",
    "source_ref": "input-3",
    "pointer": "/constraints/technical/0",
    "quote": "Python 3.12 ou superior",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-11",
    "source_ref": "input-3",
    "pointer": "/constraints/technical/1",
    "quote": "contratos versionados",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-12",
    "source_ref": "input-3",
    "pointer": "/constraints/security/0",
    "quote": "não expor dados pessoais em traces",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-13",
    "source_ref": "input-3",
    "pointer": "/constraints/business/0",
    "quote": "revisão humana antes de publicação",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-14",
    "source_ref": "input-3",
    "pointer": "/constraints/max_build_cost_usd",
    "quote": "0.0",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-15",
    "source_ref": "input-4",
    "pointer": "/backlog/0/description",
    "quote": "Permitir que o educador catalogue materiais e suas fontes.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-16",
    "source_ref": "input-5",
    "pointer": "/backlog/0/acceptance_criteria/0",
    "quote": "Cada material tem título, autor e referência de origem.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-17",
    "source_ref": "input-6",
    "pointer": "/backlog/0/acceptance_criteria/1",
    "quote": "Materiais só são visíveis ao educador responsável.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-18",
    "source_ref": "input-7",
    "pointer": "/backlog/1/description",
    "quote": "Preparar um rascunho de aula usando os materiais selecionados.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-19",
    "source_ref": "input-8",
    "pointer": "/backlog/1/acceptance_criteria/0",
    "quote": "As afirmações do rascunho referenciam os materiais utilizados.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-20",
    "source_ref": "input-9",
    "pointer": "/backlog/1/acceptance_criteria/1",
    "quote": "A publicação exige revisão e aprovação do educador.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-21",
    "source_ref": "input-10",
    "pointer": "/domain",
    "quote": "education",
    "kind": "domain-declaration",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-22",
    "source_ref": "input-11",
    "pointer": "/assets/0/path",
    "quote": "assets/brand-notes.md",
    "kind": "asset-metadata",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-23",
    "source_ref": "input-11",
    "pointer": "/assets/0/description",
    "quote": "Referência visual e verbal; conteúdo não ingerido no MVP.",
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
    "text": "Cada material tem título, autor e referência de origem.",
    "condition": "Para cada material catalogado.",
    "outcome": "O material deve ter título, autor e referência de origem.",
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação de conteúdo para todos os materiais.",
    "source_atom_ids": [
      "atom-16"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-16"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-16"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "4d2dda3c86176f06cd3e5e20fe3ca919ffe794a4f051948c4ce858c1370c4a3d"
  },
  {
    "id": "criterion-2",
    "kind": "rule",
    "text": "Materiais só são visíveis ao educador responsável.",
    "condition": "Na visualização de um material.",
    "outcome": "O material só pode ser visível ao educador responsável.",
    "exceptions": [],
    "impact": null,
    "rationale": "A presença de coordenadores pedagógicos no público não lhes concede acesso aos materiais.",
    "source_atom_ids": [
      "atom-17"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-17"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-17"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "2fb67637a1ecbf87511539a8ed5d6e23380ba265ba21b02f676fb43d5e260b50"
  },
  {
    "id": "criterion-3",
    "kind": "rule",
    "text": "As afirmações do rascunho referenciam os materiais utilizados.",
    "condition": "Para cada afirmação do rascunho.",
    "outcome": "A afirmação deve referenciar os materiais utilizados.",
    "exceptions": [],
    "impact": null,
    "rationale": "Preserva a rastreabilidade das afirmações às fontes utilizadas.",
    "source_atom_ids": [
      "atom-19"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-19"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-19"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "e093281049d61bed743966921223b9b6d2d4b38d920b40facee5294a941c3f07"
  },
  {
    "id": "criterion-4",
    "kind": "rule",
    "text": "A publicação exige revisão e aprovação do educador.",
    "condition": "Para publicar.",
    "outcome": "É necessário haver revisão e aprovação do educador.",
    "exceptions": [],
    "impact": null,
    "rationale": "Revisão e aprovação são requisitos necessários; a declaração não concede autorização suficiente por si só.",
    "source_atom_ids": [
      "atom-20"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-20"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-20"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "21e0cf0c29ba490965a10fc76f1df6d3e54782eab8514eae143c9df686c7f434"
  },
  {
    "id": "guard-human-review",
    "kind": "rule",
    "text": "Exigir revisão humana prévia.",
    "condition": "Antes de uma publicação.",
    "outcome": "Exigir revisão humana prévia.",
    "exceptions": [],
    "impact": null,
    "rationale": "Restrição geral de publicação, também expressa na concepção; não substitui a aprovação do educador exigida pelo critério.",
    "source_atom_ids": [
      "atom-13"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-13"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-13"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": "project",
    "sha256": "51acc12a15375d13edfcb4d589775a274fa18435a04915993c2f2c21c7d5756b"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar materiais e preparar aulas baseadas em fontes, com revisão humana antes da publicação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Propósito declarado da plataforma.",
    "source_atom_ids": [
      "atom-1"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "60b73f42a8932e35705a94fe16c91f66ad4ab5d149548f07f90ee5f9c5bc2c5c"
  },
  {
    "id": "context-2",
    "kind": "statement",
    "text": "Educadores e coordenadores pedagógicos.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Públicos declarados; não estabelece equivalência entre seus papéis ou permissões.",
    "source_atom_ids": [
      "atom-2",
      "atom-3"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "b4b3e960017714b84c6c13a4fe24ee8b024b7f287b7d1e631d7f5135896b5ce0"
  },
  {
    "id": "context-3",
    "kind": "statement",
    "text": "Claro, acolhedor e preciso.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Orientações de comunicação.",
    "source_atom_ids": [
      "atom-4",
      "atom-5",
      "atom-6"
    ],
    "subject": "tone",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "04225fdbb09b7069ce79ab8421421201446ee66ea030ef0ce520c18a7175f97f"
  },
  {
    "id": "context-4",
    "kind": "statement",
    "text": "Fontes verificáveis e controle do educador.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Princípios declarados do produto.",
    "source_atom_ids": [
      "atom-7",
      "atom-8"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "248b1a0b1ec05276c04ab119f0c86fa73c99d11964ee30448864b7c8872a887e"
  },
  {
    "id": "context-5",
    "kind": "domain",
    "text": "Educação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio explicitamente declarado.",
    "source_atom_ids": [
      "atom-21"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "15df5889a57397e8f0e344add115e6a34d01215e64fe2ce1b31a4a5c285ef698"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "Permitir ao educador catalogar materiais e suas fontes e preparar um rascunho de aula usando materiais selecionados.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades de apoio aos critérios.",
    "source_atom_ids": [
      "atom-15",
      "atom-18"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "82eb09121bcf340c0708a4b6759472d66023694225ce9a6d869b453edd5eb74e"
  },
  {
    "id": "context-7",
    "kind": "statement",
    "text": "A interface deve ser acessível.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita sem condição de aplicabilidade especificada; este registro não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-9"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "598b2e6de91c50e7784327acbf042a3cab8be8abe3f5d2df5e8f8a673f319a24"
  },
  {
    "id": "context-8",
    "kind": "statement",
    "text": "Usar Python 3.12 ou superior.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Restrição técnica explícita sem condição de aplicabilidade especificada.",
    "source_atom_ids": [
      "atom-10"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "dd9f4979663f4ea2de81e04055d415979b354d2f85f42ea8dfac0a3975d79819"
  },
  {
    "id": "context-9",
    "kind": "statement",
    "text": "Os contratos devem ser versionados.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita sem condição de aplicabilidade especificada; o mecanismo de versionamento não foi definido.",
    "source_atom_ids": [
      "atom-11"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "78ac1febc53116c10adf2908f4dee0f013571d7b2e87b9874a9121227604102c"
  },
  {
    "id": "context-10",
    "kind": "statement",
    "text": "Não expor dados pessoais em traces.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Proibição explícita sem gatilho de aplicabilidade especificado; permanece uma obrigação normativa.",
    "source_atom_ids": [
      "atom-12"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "0d7e02845fa8de580841a1cae54b5198f8639f7394b2abd181436888fefddf30"
  },
  {
    "id": "context-11",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado em max_build_cost_usd, sem condição de aplicabilidade especificada.",
    "source_atom_ids": [
      "atom-14"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "ba7282c6d4bb59c4ba8cc44c8a25300308315282941844522319790cfcbd091a"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "f62f9560aa2ecdebc90482158164890665a6a9d861501dc3b6fecd86b40ae5f8",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "4d2dda3c86176f06cd3e5e20fe3ca919ffe794a4f051948c4ce858c1370c4a3d",
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige título, autor e referência de origem para cada material."
    },
    {
      "finding_id": "criterion-2",
      "finding_sha256": "2fb67637a1ecbf87511539a8ed5d6e23380ba265ba21b02f676fb43d5e260b50",
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte restringe a visibilidade ao educador responsável, sem definir sua identificação."
    },
    {
      "finding_id": "criterion-3",
      "finding_sha256": "e093281049d61bed743966921223b9b6d2d4b38d920b40facee5294a941c3f07",
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige referências aos materiais utilizados nas afirmações do rascunho."
    },
    {
      "finding_id": "criterion-4",
      "finding_sha256": "21e0cf0c29ba490965a10fc76f1df6d3e54782eab8514eae143c9df686c7f434",
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Revisão e aprovação do educador são requisitos expressos para publicação."
    },
    {
      "finding_id": "guard-human-review",
      "finding_sha256": "51acc12a15375d13edfcb4d589775a274fa18435a04915993c2f2c21c7d5756b",
      "source_atom_ids": [
        "atom-13"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige revisão humana anterior à publicação; não concede autorização de publicação."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "60b73f42a8932e35705a94fe16c91f66ad4ab5d149548f07f90ee5f9c5bc2c5c",
      "source_atom_ids": [
        "atom-1"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A concepção descreve organização de materiais, aulas baseadas em fontes e revisão humana prévia."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "b4b3e960017714b84c6c13a4fe24ee8b024b7f287b7d1e631d7f5135896b5ce0",
      "source_atom_ids": [
        "atom-2",
        "atom-3"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambos os públicos estão expressos; as fontes não lhes atribuem permissões equivalentes."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "04225fdbb09b7069ce79ab8421421201446ee66ea030ef0ce520c18a7175f97f",
      "source_atom_ids": [
        "atom-4",
        "atom-5",
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os três atributos reproduzem o tom declarado."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "248b1a0b1ec05276c04ab119f0c86fa73c99d11964ee30448864b7c8872a887e",
      "source_atom_ids": [
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram verificabilidade das fontes e controle do educador."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "15df5889a57397e8f0e344add115e6a34d01215e64fe2ce1b31a4a5c285ef698",
      "source_atom_ids": [
        "atom-21"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Educação traduz o domínio declarado como education."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "82eb09121bcf340c0708a4b6759472d66023694225ce9a6d869b453edd5eb74e",
      "source_atom_ids": [
        "atom-15",
        "atom-18"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem catalogação pelo educador e preparação de rascunho com materiais selecionados."
    },
    {
      "finding_id": "context-7",
      "finding_sha256": "598b2e6de91c50e7784327acbf042a3cab8be8abe3f5d2df5e8f8a673f319a24",
      "source_atom_ids": [
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Interface acessível é uma restrição visual explícita."
    },
    {
      "finding_id": "context-8",
      "finding_sha256": "dd9f4979663f4ea2de81e04055d415979b354d2f85f42ea8dfac0a3975d79819",
      "source_atom_ids": [
        "atom-10"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição técnica estabelece Python 3.12 ou superior."
    },
    {
      "finding_id": "context-9",
      "finding_sha256": "78ac1febc53116c10adf2908f4dee0f013571d7b2e87b9874a9121227604102c",
      "source_atom_ids": [
        "atom-11"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige contratos versionados."
    },
    {
      "finding_id": "context-10",
      "finding_sha256": "0d7e02845fa8de580841a1cae54b5198f8639f7394b2abd181436888fefddf30",
      "source_atom_ids": [
        "atom-12"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte proíbe exposição de dados pessoais em traces."
    },
    {
      "finding_id": "context-11",
      "finding_sha256": "ba7282c6d4bb59c4ba8cc44c8a25300308315282941844522319790cfcbd091a",
      "source_atom_ids": [
        "atom-14"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O valor 0.0 no campo max_build_cost_usd sustenta o limite de US$ 0,00."
    }
  ],
  "component_judgments": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "note": "Cada material estabelece aplicação universal aos materiais do catálogo."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "note": "Os três campos exigidos constam expressamente."
    },
    {
      "finding_id": "criterion-2",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "note": "A fonte trata explicitamente da visibilidade dos materiais."
    },
    {
      "finding_id": "criterion-2",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "note": "Somente o educador responsável pode visualizar o material."
    },
    {
      "finding_id": "criterion-3",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "note": "A obrigação abrange as afirmações do rascunho."
    },
    {
      "finding_id": "criterion-3",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "note": "As afirmações devem referenciar os materiais utilizados."
    },
    {
      "finding_id": "criterion-4",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "note": "A publicação é o evento sujeito à exigência."
    },
    {
      "finding_id": "criterion-4",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "note": "A fonte exige conjuntamente revisão e aprovação do educador."
    },
    {
      "finding_id": "guard-human-review",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-13"
      ],
      "support": "supports",
      "note": "A fonte situa a revisão antes da publicação."
    },
    {
      "finding_id": "guard-human-review",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-13"
      ],
      "support": "supports",
      "note": "A revisão humana prévia é exigida expressamente."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Como se determina o educador responsável autorizado a visualizar cada material?",
      "rationale": "A exclusividade está definida, mas falta o critério que vincula uma pessoa ao papel responsável; isso altera quem recebe acesso.",
      "source_atom_ids": [
        "atom-17"
      ],
      "impact": "authorization"
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "Qual educador pode fornecer a revisão e aprovação exigidas para uma publicação?",
      "rationale": "A fonte exige aprovação do educador sem identificar o vínculo que habilita essa pessoa a aprovar a publicação.",
      "source_atom_ids": [
        "atom-20"
      ],
      "impact": "authorization"
    }
  ],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "6b1e42851e6b8515c7190f3acc926e4cfb328a53aaf17678156fa2350c35fe95",
      "disposition": "represented",
      "finding_ids": [
        "context-1"
      ],
      "omission_ids": [],
      "note": "Concepção integralmente representada."
    },
    {
      "atom_id": "atom-2",
      "quote_sha256": "6f9e4050f26e11615351b7b695a5f5bedd8591d0b0557c05056ae6ca7f702f50",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público educador representado."
    },
    {
      "atom_id": "atom-3",
      "quote_sha256": "caf6c915a0adb43c362a413ec22f04d1f1405cfb3f9998f4c722cc811495a14a",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público coordenador pedagógico representado."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "bdae5d555cce9e9bb1828b74b1dfa90f1c3a65d5ed322e06c3e38609b7f4823f",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom claro representado."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "5fcd5ac268c8a79c4c06d537c621653be7bfdbaf396a3ea67272b17e903ebd80",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom acolhedor representado."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "6398bad0d1c9c033b689e5356a3508389fc537bb10bdc26f0b49fa723dc90c7d",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom preciso representado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "cdcc2409dcbbd79f68e88e2e825e96687492d6f7ecff72ebaaf4eab385025f83",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Princípio de fontes verificáveis representado."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "54d11f2ad21a073d7e949afde270223730ec58eea046afb9767244b35cc586bc",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Princípio de controle do educador representado."
    },
    {
      "atom_id": "atom-9",
      "quote_sha256": "37dc387dfd2c4dcc23b99e59ae48a1baf860b032c9b7cee1bc2cd4b0d59b4742",
      "disposition": "represented",
      "finding_ids": [
        "context-7"
      ],
      "omission_ids": [],
      "note": "Obrigação de acessibilidade representada."
    },
    {
      "atom_id": "atom-10",
      "quote_sha256": "3821baa85deb28950411e56953927f45af87e0a728d986031c058603caf5e1c8",
      "disposition": "represented",
      "finding_ids": [
        "context-8"
      ],
      "omission_ids": [],
      "note": "Restrição de linguagem e versão representada."
    },
    {
      "atom_id": "atom-11",
      "quote_sha256": "6c8c51d22c903bcf20655c5144f6d989a99c35e6cf9e4951f4c8eb3b1927754d",
      "disposition": "represented",
      "finding_ids": [
        "context-9"
      ],
      "omission_ids": [],
      "note": "Obrigação de versionar contratos representada."
    },
    {
      "atom_id": "atom-12",
      "quote_sha256": "6478d143ac8b69895c72097fb00c45295bad95897de88bb4592e63b8914e1637",
      "disposition": "represented",
      "finding_ids": [
        "context-10"
      ],
      "omission_ids": [],
      "note": "Proibição de exposição em traces representada."
    },
    {
      "atom_id": "atom-13",
      "quote_sha256": "d8b7fccf2b4a31be4c721e436190f938b2f1e03ca0c4d691864ed5a1b4561f33",
      "disposition": "represented",
      "finding_ids": [
        "guard-human-review"
      ],
      "omission_ids": [],
      "note": "Restrição de revisão humana preservada separadamente."
    },
    {
      "atom_id": "atom-14",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-11"
      ],
      "omission_ids": [],
      "note": "Limite de custo representado."
    },
    {
      "atom_id": "atom-15",
      "quote_sha256": "3fb9a9c8225ab5a8fb76ef8e2b80f2bf8d752c02d5792345edc73b3124b42549",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Capacidade de catalogação representada."
    },
    {
      "atom_id": "atom-18",
      "quote_sha256": "f8a24f791bf5b85fbeaf21d5ce87a5aa89b2607a6dbf71a906872cc1d98d16dc",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Preparação de rascunho com materiais selecionados representada."
    },
    {
      "atom_id": "atom-21",
      "quote_sha256": "68bf0109c6f8a87bfa96d1ecd9503326ba35cf4a6086988a1d2c8a20fbef00d1",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Domínio representado."
    },
    {
      "atom_id": "atom-16",
      "quote_sha256": "1c22b4c7b58ee92b7c21483afc80020fd4232e80f2c81b95ff7a3e4cfd8e6f0e",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Campos obrigatórios representados."
    },
    {
      "atom_id": "atom-17",
      "quote_sha256": "87b05e3851eb9a5e12ef9326599a17b615cbd7e06106fd39df19b6ae423cbd93",
      "disposition": "missing",
      "finding_ids": [
        "criterion-2"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Restrição representada; falta esclarecer a atribuição do papel responsável."
    },
    {
      "atom_id": "atom-19",
      "quote_sha256": "ecf4bb47b217cf3dc704089e2056fd1cbffaed0ab081d1f0dec726a68d33b60e",
      "disposition": "represented",
      "finding_ids": [
        "criterion-3"
      ],
      "omission_ids": [],
      "note": "Referências das afirmações representadas."
    },
    {
      "atom_id": "atom-20",
      "quote_sha256": "6a4337aa2ca248e7621e409463d8ddb97aada7996a5684315e032b1548ae16f0",
      "disposition": "missing",
      "finding_ids": [
        "criterion-4"
      ],
      "omission_ids": [
        "omission-2"
      ],
      "note": "Requisitos representados; falta esclarecer qual educador pode aprovar."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
