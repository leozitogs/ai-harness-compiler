# Revisão do candidato v3.3 — dev-branding-conflict

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: blocked; disposição observada: blocked. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-branding-conflict",
  "baseline_selected_status": "fail",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "dca39f8f85f8c3edb38f268a0a2094a4975ef4e9a9811bba60a55d067d2eb30b",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "analysis_sha256": "f93c325ac8863bc6007a27df6d29569d768aee08346a253e3bc4806236d412b5",
  "expected_behavior": "blocked",
  "observed_disposition": "blocked",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-branding-conflict.json",
      "sha256": "b03ca50cc215814759a8b6c072eb3857ba19fefdc6487dc29674e73ec4af6530"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-branding-conflict/summary.json",
      "sha256": "00c36daee2c595e6c030df92e0f393d955a153d97e3f95fe3435d471b8387dde"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-branding-conflict/analysis.json",
      "sha256": "01fd3679abdc44bac71dc72b9fce82525b58989486ac7065369429410ff98811"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-branding-conflict/assessment.json",
      "sha256": "cfecd630eba7ef9ea87fdbcd802ee986eafd312483479a86615facd06114d8d8"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-branding-conflict/advice.json",
      "sha256": "86d4bf06d4dce3b61bccf70ba5368ea86e60a35f8e8940df37c143a502a0768f"
    }
  ],
  "findings": 9,
  "components": 2,
  "questions": [
    {
      "id": "issue-2",
      "text": "Na liberação de publicação da equipe, prevalece a dispensa de aprovação humana ou a exigência de aprovação humana explícita?",
      "impact": "precedence",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ]
    },
    {
      "id": "issue-3",
      "text": "Em quais situações é obrigatório registrar a identidade do responsável?",
      "impact": "rule",
      "source_atom_ids": [
        "atom-4"
      ]
    }
  ],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "rule",
      "text": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
      "rationale": "A declaração aparece no conflito e na pergunta de precedência, mas falta sua preservação como regra própria, sem presumir que prevaleça.",
      "source_atom_ids": [
        "atom-3"
      ],
      "impact": null
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "Quem é o responsável cuja identidade deve ser registrada?",
      "rationale": "A fonte não define esse papel; a resposta determina de quem deve ser a identidade registrada para cumprir a obrigação.",
      "source_atom_ids": [
        "atom-4"
      ],
      "impact": "outcome"
    }
  ],
  "advisory_negative_components": []
}
```

## Input completo

```json
{
  "schema_version": "ProjectInput/v1",
  "id": "dev-branding-conflict",
  "name": "Fixture dev branding-conflict",
  "conception": "Uma equipe organiza publicações e suas fontes.",
  "domain": "workspace-management",
  "branding": {
    "audience": [
      "autores"
    ],
    "tone": [],
    "principles": [
      "Liberar publicação da equipe dispensa qualquer aprovação humana."
    ],
    "visual_constraints": []
  },
  "backlog": [
    {
      "id": "register",
      "title": "Registrar e liberar",
      "description": "Organizar publicação da equipe e registrar decisões.",
      "acceptance_criteria": [
        "Liberar publicação da equipe exige aprovação humana explícita."
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
    "id": "dev-branding-conflict",
    "expected_behavior": "blocked",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "Liberar publicação da equipe exige aprovação humana explícita.",
        "disposition": "rule"
      }
    ],
    "requires_conflict": true,
    "conflict_source_pointers": [
      "/branding/principles/0",
      "/backlog/0/acceptance_criteria/0"
    ],
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
      "source_atom_id": "atom-7",
      "kind": "business-rule",
      "condition": {
        "text": "Na liberação de publicação da equipe.",
        "source_atom_ids": [
          "atom-7"
        ]
      },
      "outcome": {
        "text": "É exigida aprovação humana explícita.",
        "source_atom_ids": [
          "atom-7"
        ]
      },
      "exceptions": [],
      "note": "Regra preservada; existe uma declaração incompatível cuja precedência precisa ser definida.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar publicações da equipe, suas fontes e registrar decisões.",
      "note": "Propósito declarado na concepção e na descrição do backlog.",
      "context_indices": [
        0,
        5
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
      "subject": "domain",
      "text": "Gestão de espaços de trabalho, com organização de publicações e fontes.",
      "note": "Domínio declarado e contextualizado pela concepção.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade da obrigação não foi especificada. Esta representação preserva sua força normativa, mas não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        3
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite declarado em max_build_cost_usd.",
      "context_indices": [
        4
      ]
    }
  ],
  "issues": [
    {
      "kind": "conflict",
      "text": "Uma declaração dispensa qualquer aprovação humana para liberar publicação da equipe, enquanto o critério exige aprovação humana explícita para a mesma operação.",
      "context_indices": [
        2,
        7
      ],
      "rationale": "As duas declarações estabelecem exigências incompatíveis para a liberação, sem precedência definida.",
      "impact": null,
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Na liberação de publicação da equipe, prevalece a dispensa de aprovação humana ou a exigência de aprovação humana explícita?",
      "context_indices": [
        2,
        7
      ],
      "rationale": "A decisão determina se a publicação pode ser liberada sem aprovação humana.",
      "impact": "precedence",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Em quais situações é obrigatório registrar a identidade do responsável?",
      "context_indices": [
        3
      ],
      "rationale": "A obrigação foi declarada sem aplicabilidade; definir seu alcance determina quando a ausência do registro constitui descumprimento.",
      "impact": "rule",
      "rejection_reason": null
    }
  ]
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
    "quote": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-4",
    "source_ref": "input-3",
    "pointer": "/constraints/business/0",
    "quote": "Registrar a identidade do responsável.",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-5",
    "source_ref": "input-3",
    "pointer": "/constraints/max_build_cost_usd",
    "quote": "0.0",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-6",
    "source_ref": "input-4",
    "pointer": "/backlog/0/description",
    "quote": "Organizar publicação da equipe e registrar decisões.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-7",
    "source_ref": "input-5",
    "pointer": "/backlog/0/acceptance_criteria/0",
    "quote": "Liberar publicação da equipe exige aprovação humana explícita.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-8",
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
    "text": "Liberar publicação da equipe exige aprovação humana explícita.",
    "condition": "Na liberação de publicação da equipe.",
    "outcome": "É exigida aprovação humana explícita.",
    "exceptions": [],
    "impact": null,
    "rationale": "Regra preservada; existe uma declaração incompatível cuja precedência precisa ser definida.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-7"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-7"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "83927f49eaf90ec557c92fb8de3c44b191d4a318e121c7076a971bc8e3c82938"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar publicações da equipe, suas fontes e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Propósito declarado na concepção e na descrição do backlog.",
    "source_atom_ids": [
      "atom-1",
      "atom-6"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "a8729c31d0316a67f00942ee655e6981dc7ca14b58e4e5415472dd39bda6b3b6"
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
    "kind": "domain",
    "text": "Gestão de espaços de trabalho, com organização de publicações e fontes.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio declarado e contextualizado pela concepção.",
    "source_atom_ids": [
      "atom-1",
      "atom-8"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "fe2d770b86460b84c003624ee2d6d8bf8c55d1132333b1bc658104cb5eb564c5"
  },
  {
    "id": "context-4",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade da obrigação não foi especificada. Esta representação preserva sua força normativa, mas não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-4"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "312fa51ca6d3ff556a57ed6f9ef2035fe6c2456f98e4d6cd1440a4ee54f69247"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado em max_build_cost_usd.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "66b1447ebd4661c459763654d13d57d5de7bcbe4cc8b566e59618f9d0a04bc4c"
  },
  {
    "id": "issue-1",
    "kind": "conflict",
    "text": "Uma declaração dispensa qualquer aprovação humana para liberar publicação da equipe, enquanto o critério exige aprovação humana explícita para a mesma operação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "As duas declarações estabelecem exigências incompatíveis para a liberação, sem precedência definida.",
    "source_atom_ids": [
      "atom-3",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "1adf03a6451b1d7a3dd38c433e68c8762921bb5b2807b849c567643b9ea112b8"
  },
  {
    "id": "issue-2",
    "kind": "question",
    "text": "Na liberação de publicação da equipe, prevalece a dispensa de aprovação humana ou a exigência de aprovação humana explícita?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "precedence",
    "rationale": "A decisão determina se a publicação pode ser liberada sem aprovação humana.",
    "source_atom_ids": [
      "atom-3",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "9713ce42665fb42014bec91ac0034a763b3a4e7d1d1248e957dc0991c06f4b23"
  },
  {
    "id": "issue-3",
    "kind": "question",
    "text": "Em quais situações é obrigatório registrar a identidade do responsável?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "rule",
    "rationale": "A obrigação foi declarada sem aplicabilidade; definir seu alcance determina quando a ausência do registro constitui descumprimento.",
    "source_atom_ids": [
      "atom-4"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "df2acf0aa9d3aad12b39e556754e7160db5afd207a5f5fd55aca210b8d7721fc"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "f93c325ac8863bc6007a27df6d29569d768aee08346a253e3bc4806236d412b5",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "83927f49eaf90ec557c92fb8de3c44b191d4a318e121c7076a971bc8e3c82938",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O critério exige expressamente aprovação humana explícita para liberar publicação da equipe; isso não resolve a precedência."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "a8729c31d0316a67f00942ee655e6981dc7ca14b58e4e5415472dd39bda6b3b6",
      "source_atom_ids": [
        "atom-1",
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A concepção inclui publicações e fontes; o backlog acrescenta registrar decisões."
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
      "finding_sha256": "fe2d770b86460b84c003624ee2d6d8bf8c55d1132333b1bc658104cb5eb564c5",
      "source_atom_ids": [
        "atom-1",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio declarado e a concepção sustentam gestão de espaços de trabalho com publicações e fontes."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "312fa51ca6d3ff556a57ed6f9ef2035fe6c2456f98e4d6cd1440a4ee54f69247",
      "source_atom_ids": [
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição determina registrar a identidade do responsável, sem definir aplicabilidade ou identificar esse papel."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "66b1447ebd4661c459763654d13d57d5de7bcbe4cc8b566e59618f9d0a04bc4c",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd contém 0.0."
    },
    {
      "finding_id": "issue-1",
      "finding_sha256": "1adf03a6451b1d7a3dd38c433e68c8762921bb5b2807b849c567643b9ea112b8",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes dispensam e exigem aprovação humana para a mesma operação, sem estabelecer precedência."
    },
    {
      "finding_id": "issue-2",
      "finding_sha256": "9713ce42665fb42014bec91ac0034a763b3a4e7d1d1248e957dc0991c06f4b23",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "Resolver a incompatibilidade determina se a liberação exige aprovação humana."
    },
    {
      "finding_id": "issue-3",
      "finding_sha256": "df2acf0aa9d3aad12b39e556754e7160db5afd207a5f5fd55aca210b8d7721fc",
      "source_atom_ids": [
        "atom-4"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "A restrição não explicita quando o registro é obrigatório; seu alcance altera a aplicação da regra."
    }
  ],
  "component_judgments": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "note": "A fonte identifica a liberação de publicação da equipe."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "note": "A fonte exige aprovação humana explícita."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "rule",
      "text": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
      "rationale": "A declaração aparece no conflito e na pergunta de precedência, mas falta sua preservação como regra própria, sem presumir que prevaleça.",
      "source_atom_ids": [
        "atom-3"
      ],
      "impact": null
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "Quem é o responsável cuja identidade deve ser registrada?",
      "rationale": "A fonte não define esse papel; a resposta determina de quem deve ser a identidade registrada para cumprir a obrigação.",
      "source_atom_ids": [
        "atom-4"
      ],
      "impact": "outcome"
    }
  ],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "88b9866f0e0b53ae15c7d6439e0c540ac09134f17f179c297c4dde265f0c01eb",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "context-3"
      ],
      "omission_ids": [],
      "note": "Concepção representada no propósito e no domínio."
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
      "quote_sha256": "0ba17f24c70a64bbb5fd194039a4ba51895bf4658effd0fa2b914c5deea3a9e3",
      "disposition": "missing",
      "finding_ids": [
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Conflito e precedência representados; falta a regra autônoma de dispensa."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "missing",
      "finding_ids": [
        "context-4",
        "issue-3"
      ],
      "omission_ids": [
        "omission-2"
      ],
      "note": "Obrigação e dúvida de aplicabilidade preservadas; falta esclarecer a identidade exigida."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Limite de custo preservado."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-1"
      ],
      "omission_ids": [],
      "note": "Organização e registro de decisões preservados."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "d8ec0dfaccceaea0a5f8ccf5a95f094560df5ea36683833d84877c601223e217",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Domínio preservado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "61b8ffef4cf839d5f9ae757a387e5b7fbd53d3468c647d8cd23bf258c29e55d3",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Exigência, conflito e dúvida de precedência preservados."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
