# Revisão do candidato v3.4 — dev-branding-conflict

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
  "previous_round_status": "fail",
  "previous_round_analysis_sha256": "f93c325ac8863bc6007a27df6d29569d768aee08346a253e3bc4806236d412b5",
  "identical_to_previous_round": false,
  "analysis_sha256": "1e31df44f4622121c3574bcc417e6e1050e90cf80ff4f5cf553ce207ef6aaefc",
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
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-branding-conflict/summary.json",
      "sha256": "00c36daee2c595e6c030df92e0f393d955a153d97e3f95fe3435d471b8387dde"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-branding-conflict/analysis.json",
      "sha256": "385edf600176bb23ee58948e32f6f341bf0eb0c1235b4a942fbcae8dbff98cdf"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-branding-conflict/assessment.json",
      "sha256": "1e4b6d90432f015fa1fb26cda92aea03c145c22966e2bc2d12ff8f13dff79b4f"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-branding-conflict/advice.json",
      "sha256": "1969d6160f87ca868a32de6ac7dc30a34fc0c38cf0242b2a5755d382e7811c3c"
    }
  ],
  "findings": 9,
  "components": 2,
  "questions": [
    {
      "id": "issue-2",
      "text": "Qual declaração prevalece para liberar publicação da equipe: a dispensa de qualquer aprovação humana ou a exigência de aprovação humana explícita?",
      "impact": "precedence",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ]
    }
  ],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "rule",
      "text": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
      "rationale": "A dispensa aparece no conflito e na pergunta, mas falta como regra independente, preservada sem resolver a precedência.",
      "source_atom_ids": [
        "atom-3"
      ],
      "impact": null
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "A quais operações se aplica a obrigação de registrar a identidade do responsável?",
      "rationale": "A obrigação está preservada, mas seu âmbito não foi definido; a resposta altera a aplicabilidade da regra, além de detalhes de implementação.",
      "source_atom_ids": [
        "atom-4"
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
        "text": "Ao liberar publicação da equipe.",
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
      "note": "Regra preservada; existe declaração incompatível sobre a exigência de aprovação.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar publicações da equipe e suas fontes.",
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
      "subject": "capability",
      "text": "Organizar publicação da equipe e registrar decisões.",
      "note": "Capacidades declaradas no backlog.",
      "context_indices": [
        5
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de workspace.",
      "note": "Domínio declarado como workspace-management.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "Registrar a identidade do responsável.",
      "note": "Obrigação explícita cuja aplicabilidade não foi especificada. Preservá-la como contexto normativo não estabelece uma política executável de aplicabilidade; a ausência de mecanismo ou momento de registro não torna a obrigação indeterminada.",
      "context_indices": [
        3
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de build é US$ 0,00.",
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
      "rationale": "As duas declarações estabelecem obrigações incompatíveis sobre a mesma liberação; não foi definida precedência.",
      "impact": null,
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Qual declaração prevalece para liberar publicação da equipe: a dispensa de qualquer aprovação humana ou a exigência de aprovação humana explícita?",
      "context_indices": [
        2,
        7
      ],
      "rationale": "A decisão determina se a liberação depende de aprovação humana; sem precedência, a condição de autorização permanece indefinida.",
      "impact": "precedence",
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
    "condition": "Ao liberar publicação da equipe.",
    "outcome": "É exigida aprovação humana explícita.",
    "exceptions": [],
    "impact": null,
    "rationale": "Regra preservada; existe declaração incompatível sobre a exigência de aprovação.",
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
    "sha256": "a46154d7baaeda81be07bf850bdd4e161e617029b5b437c603eb3162ce8eb237"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar publicações da equipe e suas fontes.",
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
    "sha256": "51c260baca8628898ac93bc9d5eda2c0266bd567b74de17d56a231af4f87687e"
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
    "text": "Organizar publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades declaradas no backlog.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "4cf342f2e69bd45e675f0858e47f8b3934b3299dc45697234f8501854acf3841"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de workspace.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio declarado como workspace-management.",
    "source_atom_ids": [
      "atom-8"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "3bca78c822726896f2d0d5133d22f4d9bd541b38d08bfce5ef6d29e71d96c445"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita cuja aplicabilidade não foi especificada. Preservá-la como contexto normativo não estabelece uma política executável de aplicabilidade; a ausência de mecanismo ou momento de registro não torna a obrigação indeterminada.",
    "source_atom_ids": [
      "atom-4"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "f82daf3c55e4d01b5fc21dc51a7a699256bb471a959eaef982ac8d3a3f2e790b"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de build é US$ 0,00.",
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
    "sha256": "4b31ec63965dd859de82ad4a2036653cb25d5e383f7bf64ea13e88bd223072b1"
  },
  {
    "id": "issue-1",
    "kind": "conflict",
    "text": "Uma declaração dispensa qualquer aprovação humana para liberar publicação da equipe, enquanto o critério exige aprovação humana explícita para a mesma operação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "As duas declarações estabelecem obrigações incompatíveis sobre a mesma liberação; não foi definida precedência.",
    "source_atom_ids": [
      "atom-3",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "905b917303b75222e75dac853eef84523d989a60ff6e8787f193bd2e9b6364ca"
  },
  {
    "id": "issue-2",
    "kind": "question",
    "text": "Qual declaração prevalece para liberar publicação da equipe: a dispensa de qualquer aprovação humana ou a exigência de aprovação humana explícita?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "precedence",
    "rationale": "A decisão determina se a liberação depende de aprovação humana; sem precedência, a condição de autorização permanece indefinida.",
    "source_atom_ids": [
      "atom-3",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "6dee074d47d96848fc3b87f89906ba6e5f5ba90a950f76c37cfd98b080dbae25"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "1e31df44f4622121c3574bcc417e6e1050e90cf80ff4f5cf553ce207ef6aaefc",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "a46154d7baaeda81be07bf850bdd4e161e617029b5b437c603eb3162ce8eb237",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige expressamente aprovação humana explícita para liberar publicação da equipe."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "51c260baca8628898ac93bc9d5eda2c0266bd567b74de17d56a231af4f87687e",
      "source_atom_ids": [
        "atom-1"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A concepção descreve a organização de publicações e suas fontes por uma equipe."
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
      "finding_sha256": "4cf342f2e69bd45e675f0858e47f8b3934b3299dc45697234f8501854acf3841",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A descrição do backlog declara ambas as capacidades."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "3bca78c822726896f2d0d5133d22f4d9bd541b38d08bfce5ef6d29e71d96c445",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Gestão de workspace corresponde ao domínio workspace-management."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "f82daf3c55e4d01b5fc21dc51a7a699256bb471a959eaef982ac8d3a3f2e790b",
      "source_atom_ids": [
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige registrar a identidade do responsável, sem definir aplicabilidade ou equipará-lo ao executor."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "4b31ec63965dd859de82ad4a2036653cb25d5e383f7bf64ea13e88bd223072b1",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd estabelece limite de zero dólares."
    },
    {
      "finding_id": "issue-1",
      "finding_sha256": "905b917303b75222e75dac853eef84523d989a60ff6e8787f193bd2e9b6364ca",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes dispensam e exigem aprovação humana para a mesma operação, sem precedência declarada."
    },
    {
      "finding_id": "issue-2",
      "finding_sha256": "6dee074d47d96848fc3b87f89906ba6e5f5ba90a950f76c37cfd98b080dbae25",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "Resolver a precedência determina se a liberação depende de aprovação humana."
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
      "note": "A operação expressa na fonte é liberar publicação da equipe."
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
      "rationale": "A dispensa aparece no conflito e na pergunta, mas falta como regra independente, preservada sem resolver a precedência.",
      "source_atom_ids": [
        "atom-3"
      ],
      "impact": null
    },
    {
      "id": "omission-2",
      "kind": "question",
      "text": "A quais operações se aplica a obrigação de registrar a identidade do responsável?",
      "rationale": "A obrigação está preservada, mas seu âmbito não foi definido; a resposta altera a aplicabilidade da regra, além de detalhes de implementação.",
      "source_atom_ids": [
        "atom-4"
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
        "context-1"
      ],
      "omission_ids": [],
      "note": "Concepção preservada."
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
      "note": "Conflito e precedência representados; falta preservar a dispensa como regra."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "missing",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [
        "omission-2"
      ],
      "note": "Obrigação preservada; falta esclarecer seu âmbito de aplicação."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Limite de custo preservado."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Ambas as capacidades preservadas."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "d8ec0dfaccceaea0a5f8ccf5a95f094560df5ea36683833d84877c601223e217",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
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
      "note": "Exigência, conflito e questão de precedência preservados."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
