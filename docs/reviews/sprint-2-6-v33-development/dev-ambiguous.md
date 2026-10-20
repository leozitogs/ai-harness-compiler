# Revisão do candidato v3.3 — dev-ambiguous

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: blocked; disposição observada: blocked. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-ambiguous",
  "baseline_selected_status": "fail",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "44f9c5bbb4d4461109433ede9bddcbb99b27131c08af8714d6fd314fd86adc54",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "analysis_sha256": "a6ae3a4dc18bfcb8bfc52aa69e2eaeb6683e3e2155cd2a42335e87ed5d1598f4",
  "expected_behavior": "blocked",
  "observed_disposition": "blocked",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-ambiguous.json",
      "sha256": "b4b91de66473ba2ce628faae3aefddc571213af16ae08a34c00ef2f2440df3ae"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-ambiguous/summary.json",
      "sha256": "8ee1fdb3c96e688e8d6b6af20aa5d0780fc0f78a7625123cc05c3342eee9d309"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-ambiguous/analysis.json",
      "sha256": "fbf08d9d2ba876f0e1771821b93eb95ddc0e0615c11459600ed633f9a5ad8b99"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-ambiguous/assessment.json",
      "sha256": "014ef308b60eff4000daf2874476fe3ff48e75b0c8819cbeb1ca06dc9e5ea560"
    },
    {
      "path": "docs/evidence/sprint-2-6-v33-development-20261020/execution/dev-ambiguous/advice.json",
      "sha256": "016142b1279e2c3d651342d7af6bb3ce9c6ac2cf6dbfcfb61a5f0472d1a3d48b"
    }
  ],
  "findings": 11,
  "components": 2,
  "questions": [
    {
      "id": "issue-1",
      "text": "Quais etapas e condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
      "impact": "outcome",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ]
    },
    {
      "id": "issue-2",
      "text": "Como se distribuem os papéis e as autorizações no processo de publicação, considerando que a confirmação cabe ao operador?",
      "impact": "authorization",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ]
    },
    {
      "id": "issue-3",
      "text": "Em quais situações deve ser registrada a identidade do responsável, e por qual atividade essa pessoa responde?",
      "impact": "rule",
      "source_atom_ids": [
        "atom-5"
      ]
    }
  ],
  "guards": [],
  "advisory_omissions": [],
  "advisory_negative_components": []
}
```

## Input completo

```json
{
  "schema_version": "ProjectInput/v1",
  "id": "dev-ambiguous",
  "name": "Fixture dev ambiguous",
  "conception": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
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
        "O operador confirma publicação da equipe antes de concluir."
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
    "id": "dev-ambiguous",
    "expected_behavior": "blocked",
    "obligations": [
      {
        "id": "required-1",
        "source_pointer": "/backlog/0/acceptance_criteria/0",
        "quote": "O operador confirma publicação da equipe antes de concluir.",
        "disposition": "rule"
      },
      {
        "id": "completion-definition",
        "source_pointer": "/conception",
        "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
        "disposition": "required-question"
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
        "text": "Antes de concluir.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "outcome": {
        "text": "O operador deve confirmar a publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "exceptions": [],
      "note": "A confirmação é obrigatória antes da conclusão, mas não estabelece, por si só, todas as condições de conclusão.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Melhorar o processo de publicação da equipe e registrar decisões.",
      "note": "Finalidade inferida da concepção e da descrição do backlog.",
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
      "text": "Rastreabilidade e controle humano.",
      "note": "Princípios declarados para orientar o projeto.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Organização da publicação da equipe.",
      "note": "Não há indicação do tipo de conteúdo publicado.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "capability",
      "text": "Registrar decisões.",
      "note": "Capacidade explícita; o formato do registro não foi especificado.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade da obrigação não foi especificada. Esta representação preserva a obrigação, mas não fornece uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é USD 0,00.",
      "note": "Limite declarado pelo campo max_build_cost_usd.",
      "context_indices": [
        5
      ]
    }
  ],
  "issues": [
    {
      "kind": "question",
      "text": "Quais etapas e condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
      "context_indices": [
        0,
        6,
        7
      ],
      "rationale": "A concepção declara etapas e condições de conclusão indefinidas. O critério estabelece uma confirmação prévia obrigatória, mas não permite determinar quando o processo pode ser considerado concluído.",
      "impact": "outcome",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Como se distribuem os papéis e as autorizações no processo de publicação, considerando que a confirmação cabe ao operador?",
      "context_indices": [
        0,
        6,
        7
      ],
      "rationale": "Os papéis estão explicitamente indefinidos. A atribuição da confirmação ao operador não define a autoridade sobre as demais etapas do processo.",
      "impact": "authorization",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Em quais situações deve ser registrada a identidade do responsável, e por qual atividade essa pessoa responde?",
      "context_indices": [
        4
      ],
      "rationale": "A obrigação é explícita, mas não identifica sua aplicabilidade nem o vínculo de responsabilidade. Essas definições alteram quando o registro é exigido e o que satisfaz a obrigação.",
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
    "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
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
    "quote": "O operador confirma publicação da equipe antes de concluir.",
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
    "text": "O operador confirma publicação da equipe antes de concluir.",
    "condition": "Antes de concluir.",
    "outcome": "O operador deve confirmar a publicação da equipe.",
    "exceptions": [],
    "impact": null,
    "rationale": "A confirmação é obrigatória antes da conclusão, mas não estabelece, por si só, todas as condições de conclusão.",
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
    "sha256": "baca34c43ed68b8a3462221e3546ed44d0056ed7ad487d62b823f6cca3c0408a"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Melhorar o processo de publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Finalidade inferida da concepção e da descrição do backlog.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "bd421b12e98220b4a0ce807e95a59fe04c161ba47ceaa94edd0806d543762243"
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
    "text": "Organização da publicação da equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Não há indicação do tipo de conteúdo publicado.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "735f7ebc0cdcde3679ce4041ffb65822307ead94d7c8b70b4397e295ddec8a16"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "Registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidade explícita; o formato do registro não foi especificado.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "be12b65118e52fd2cd8440b9b953b85713938a2646fc5502813b28be04a5c630"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade da obrigação não foi especificada. Esta representação preserva a obrigação, mas não fornece uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "5d057a465d6aefe7127bf5d4756c424a1e47f818fd1a311e3c04cdbcd63ad1a7"
  },
  {
    "id": "context-7",
    "kind": "statement",
    "text": "O custo máximo de construção é USD 0,00.",
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
    "sha256": "af7b2a0e2ed2d6027fa002f0656a27ab3ce60f735a8e2f4a09877707e2c698f7"
  },
  {
    "id": "issue-1",
    "kind": "question",
    "text": "Quais etapas e condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "outcome",
    "rationale": "A concepção declara etapas e condições de conclusão indefinidas. O critério estabelece uma confirmação prévia obrigatória, mas não permite determinar quando o processo pode ser considerado concluído.",
    "source_atom_ids": [
      "atom-1",
      "atom-7",
      "atom-8"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "170f1c7c3a18e7b3d8bc3121c2bb70d77fac2b4f5b57cb1df54fed65ea1bfd34"
  },
  {
    "id": "issue-2",
    "kind": "question",
    "text": "Como se distribuem os papéis e as autorizações no processo de publicação, considerando que a confirmação cabe ao operador?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "authorization",
    "rationale": "Os papéis estão explicitamente indefinidos. A atribuição da confirmação ao operador não define a autoridade sobre as demais etapas do processo.",
    "source_atom_ids": [
      "atom-1",
      "atom-7",
      "atom-8"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "24eaa99ab790ec14b6bfe9a0050369bc6a5ea93593ee202f1c9d92cb4e48ce2a"
  },
  {
    "id": "issue-3",
    "kind": "question",
    "text": "Em quais situações deve ser registrada a identidade do responsável, e por qual atividade essa pessoa responde?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "rule",
    "rationale": "A obrigação é explícita, mas não identifica sua aplicabilidade nem o vínculo de responsabilidade. Essas definições alteram quando o registro é exigido e o que satisfaz a obrigação.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "b8f0609a97cea993c0d18a05eb68abf9fd8d7df16eb44502ca31e322c40f1ad6"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "a6ae3a4dc18bfcb8bfc52aa69e2eaeb6683e3e2155cd2a42335e87ed5d1598f4",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "baca34c43ed68b8a3462221e3546ed44d0056ed7ad487d62b823f6cca3c0408a",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O critério exige a confirmação pelo operador antes de concluir, sem definir outras condições de conclusão."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "bd421b12e98220b4a0ce807e95a59fe04c161ba47ceaa94edd0806d543762243",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A concepção pede melhoria do processo; o backlog identifica publicação da equipe e registro de decisões."
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
      "finding_sha256": "99f9e7b91f43bfee9ea5de9d19676e55ab7742a6ac72f07fbb1a041b28f03deb",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os princípios declarados são rastreabilidade e controle humano."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "735f7ebc0cdcde3679ce4041ffb65822307ead94d7c8b70b4397e295ddec8a16",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O backlog declara organizar a publicação da equipe, sem especificar o conteúdo."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "be12b65118e52fd2cd8440b9b953b85713938a2646fc5502813b28be04a5c630",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Registrar decisões é uma capacidade explícita do backlog."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "5d057a465d6aefe7127bf5d4756c424a1e47f818fd1a311e3c04cdbcd63ad1a7",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável; não define aplicabilidade nem equipara responsável a operador."
    },
    {
      "finding_id": "context-7",
      "finding_sha256": "af7b2a0e2ed2d6027fa002f0656a27ab3ce60f735a8e2f4a09877707e2c698f7",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd contém 0.0, sustentando o limite declarado."
    },
    {
      "finding_id": "issue-1",
      "finding_sha256": "170f1c7c3a18e7b3d8bc3121c2bb70d77fac2b4f5b57cb1df54fed65ea1bfd34",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "Etapas e condições de conclusão estão explicitamente indefinidas; a confirmação prévia não resolve quando concluir."
    },
    {
      "finding_id": "issue-2",
      "finding_sha256": "24eaa99ab790ec14b6bfe9a0050369bc6a5ea93593ee202f1c9d92cb4e48ce2a",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "Os papéis estão indefinidos; atribuir confirmação ao operador não estabelece as demais autorizações."
    },
    {
      "finding_id": "issue-3",
      "finding_sha256": "b8f0609a97cea993c0d18a05eb68abf9fd8d7df16eb44502ca31e322c40f1ad6",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "A restrição não identifica situações de aplicação nem a atividade do responsável, afetando a satisfação da obrigação."
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
      "note": "A expressão antes de concluir estabelece o momento da exigência."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "O critério atribui ao operador a confirmação da publicação da equipe."
    }
  ],
  "omissions": [],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "12c881ea64cc68b9aaf7a45d4f29375b8d95498dbb4859448f7c857eb0f202c8",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Melhoria pretendida e indefinições de etapas, papéis e conclusão estão representadas."
    },
    {
      "atom_id": "atom-2",
      "quote_sha256": "75f26d13ebd8877644c57a369ce71b82b639903217ed12ebe61beeffd8c11586",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público declarado representado."
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
      "note": "Princípio de controle humano representado, sem inferir autoridade específica."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "represented",
      "finding_ids": [
        "context-6",
        "issue-3"
      ],
      "omission_ids": [],
      "note": "Obrigação de identidade e sua aplicabilidade indefinida estão representadas separadamente da confirmação."
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
        "context-4",
        "context-5",
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Organização da publicação e registro de decisões representados; questões usam esse escopo."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "c52f9dd3da88167ffe7a9e1bf99a6efa142a0bb83392caacb04c20e3d767b055",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Confirmação prévia pelo operador representada, preservando dúvidas sobre conclusão e demais autorizações."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
