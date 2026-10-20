# Revisão do candidato v3.3 — dev-rules-a

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
  "analysis_sha256": "0322100803ba35de424ff2d70921a770eddbe317b66c61c86f10a6efbd2bbc34",
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
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-rules-a/summary.json",
      "sha256": "91d31b8311bfbf755336cd1d67d146457d2b50f2c24205a9d91eb2ce723b4401"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-rules-a/analysis.json",
      "sha256": "fa368ada7d60b13f0360b62334ac516560035b382fdc9f490f8e5336bab1eea9"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-rules-a/assessment.json",
      "sha256": "1fe330a3b0f0a0d5b5d873e57ec8371e311ace7408f83c68517fce0ba209daf5"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-rules-a/advice.json",
      "sha256": "4bfeb7703612351e9afb5dd3b884bbf69bd74f403df5cfa4b17f288a276e0a55"
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
      "text": "Em quais situações é obrigatório registrar a identidade e qual papel define o responsável nesse registro?",
      "rationale": "A obrigação está preservada, mas seu alcance e sujeito permanecem indefinidos; esclarecê-los altera a aplicação da regra de registro.",
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
        "text": "Para liberar uma publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "outcome": {
        "text": "É obrigatória a aprovação do responsável designado.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "exceptions": [],
      "note": "A aprovação é uma condição necessária; o texto não declara que ela seja suficiente para liberar a publicação.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Apoiar uma equipe na organização de publicações e suas fontes e no registro de decisões.",
      "note": "Finalidade declarada na concepção e na descrição do backlog.",
      "context_indices": [
        0,
        6
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
      "note": "Esses princípios não especificam procedimentos adicionais de aprovação.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de espaços de trabalho, com organização de publicações, fontes e decisões da equipe.",
      "note": "Combina o domínio declarado com o escopo descrito.",
      "context_indices": [
        0,
        6,
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade dessa obrigação não foi especificada. Ela é preservada como obrigação normativa, sem fornecer uma política executável de aplicabilidade nem presumir que esse responsável seja o responsável designado para aprovar publicações.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é de US$ 0,00.",
      "note": "Limite declarado em max_build_cost_usd.",
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
    "condition": "Para liberar uma publicação da equipe.",
    "outcome": "É obrigatória a aprovação do responsável designado.",
    "exceptions": [],
    "impact": null,
    "rationale": "A aprovação é uma condição necessária; o texto não declara que ela seja suficiente para liberar a publicação.",
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
    "sha256": "2113c05cf869d630d2ee86b2ab5920f73c4c189cf000a0a95dc8fc575be5eca4"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Apoiar uma equipe na organização de publicações e suas fontes e no registro de decisões.",
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
    "sha256": "8fba25e995733a041708025f345706c134021b33ebab8d78c0bad1671bc295db"
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
    "rationale": "Esses princípios não especificam procedimentos adicionais de aprovação.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "1aa63a86b9bd2861508f9618aa798aec93bcb4b59b2fc30b575eece919146312"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de espaços de trabalho, com organização de publicações, fontes e decisões da equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Combina o domínio declarado com o escopo descrito.",
    "source_atom_ids": [
      "atom-1",
      "atom-7",
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "586465635cdf333c5997db726d07679002e5c3b31664dc4fe1f85fe208424f5a"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade dessa obrigação não foi especificada. Ela é preservada como obrigação normativa, sem fornecer uma política executável de aplicabilidade nem presumir que esse responsável seja o responsável designado para aprovar publicações.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "edeb1a6bd93d3fb407e4f40872b0fbc81a933f98fcfe6d15fe53f5538a9d41db"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de construção é de US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado em max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "7c74b8abaf3b3816f12c4c57e5c15bc1b81fe414e5cfdf0b2c769e9e73fb242c"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "0322100803ba35de424ff2d70921a770eddbe317b66c61c86f10a6efbd2bbc34",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "2113c05cf869d630d2ee86b2ab5920f73c4c189cf000a0a95dc8fc575be5eca4",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige aprovação do responsável designado para liberar a publicação, sem afirmar suficiência."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "8fba25e995733a041708025f345706c134021b33ebab8d78c0bad1671bc295db",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem organização de publicações e fontes e registro de decisões."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O público declarado é autores."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "1aa63a86b9bd2861508f9618aa798aec93bcb4b59b2fc30b575eece919146312",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os dois princípios são explicitamente declarados."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "586465635cdf333c5997db726d07679002e5c3b31664dc4fe1f85fe208424f5a",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio declarado e as atividades descritas sustentam a síntese."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "edeb1a6bd93d3fb407e4f40872b0fbc81a933f98fcfe6d15fe53f5538a9d41db",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável; não define aplicabilidade nem concede autorização."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "7c74b8abaf3b3816f12c4c57e5c15bc1b81fe414e5cfdf0b2c769e9e73fb242c",
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
      "note": "A fonte situa a exigência na liberação de publicação da equipe."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A fonte exige expressamente aprovação do responsável designado."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Em quais situações é obrigatório registrar a identidade e qual papel define o responsável nesse registro?",
      "rationale": "A obrigação está preservada, mas seu alcance e sujeito permanecem indefinidos; esclarecê-los altera a aplicação da regra de registro.",
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
      "note": "Princípio representado sem inferir procedimentos."
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
      "note": "Obrigação representada; falta questão material sobre alcance e sujeito."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Limite financeiro representado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "context-4"
      ],
      "omission_ids": [],
      "note": "Atividades descritas representadas."
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
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Exigência de aprovação representada; não vincula o aprovador ao responsável pelo registro."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
