# Revisão do candidato v3.4 — dev-ambiguous

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
  "previous_round_status": "fail",
  "previous_round_analysis_sha256": "a6ae3a4dc18bfcb8bfc52aa69e2eaeb6683e3e2155cd2a42335e87ed5d1598f4",
  "identical_to_previous_round": false,
  "analysis_sha256": "7e552b1881ef697bac14441cb3002defeb5899125cb706fba093edfc3100709f",
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
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-ambiguous/summary.json",
      "sha256": "c38c803b1e78e2dbf29c5786516306e2d64a023cff13d76003f0bd75694dbd15"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-ambiguous/analysis.json",
      "sha256": "b34a010ece573ba76f924427f692a8700ca3f473ef6520384f8b7197a43fbb48"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-ambiguous/assessment.json",
      "sha256": "d3294808aba67ccb9802703fce2e4511868d4fd32c6d434eff8f67887175c0cc"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-ambiguous/advice.json",
      "sha256": "f32114e1a8c928d56dbb4817b44c99c7df2e0326719f430e3267e30688a04ac7"
    }
  ],
  "findings": 9,
  "components": 2,
  "questions": [
    {
      "id": "issue-1",
      "text": "Quais condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
      "impact": "outcome",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ]
    },
    {
      "id": "issue-2",
      "text": "Quais etapas e papéis devem compor o processo de organização da publicação e registro de decisões?",
      "impact": "implementation-detail",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ]
    }
  ],
  "guards": [],
  "advisory_omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Em quais situações é obrigatório registrar a identidade e quem deve ser identificado como responsável?",
      "rationale": "A restrição não define sua aplicabilidade nem o responsável. Essas respostas determinam quando e de quem o registro é exigido; não se pode presumir que seja o operador.",
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
      "note": "A confirmação é obrigatória antes da conclusão; o critério não estabelece que ela seja suficiente para concluir.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Melhorar o processo de publicação da equipe e registrar decisões.",
      "note": "As etapas, os papéis e as condições de conclusão foram declarados indefinidos.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "audience",
      "text": "Autores.",
      "note": "Público explicitamente indicado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano são princípios do projeto.",
      "note": "Esses princípios não estabelecem permissões ou aprovações adicionais.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar a publicação da equipe e registrar decisões.",
      "note": "Capacidades declaradas em termos amplos.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A aplicabilidade não foi especificada. A obrigação é preservada sem atribuir um gatilho, equiparar o responsável ao operador ou estabelecer uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de build é US$ 0,00.",
      "note": "Limite explícito de custo.",
      "context_indices": [
        5
      ]
    }
  ],
  "issues": [
    {
      "kind": "question",
      "text": "Quais condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
      "context_indices": [
        0,
        6,
        7
      ],
      "rationale": "As condições de conclusão estão explicitamente indefinidas. A confirmação estabelece uma obrigação prévia, mas não determina quando o processo pode ser considerado concluído.",
      "impact": "outcome",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Quais etapas e papéis devem compor o processo de organização da publicação e registro de decisões?",
      "context_indices": [
        0,
        6
      ],
      "rationale": "Etapas e papéis foram declarados indefinidos; seu detalhamento auxilia a implementação, sem alterar por si só a obrigação conhecida de confirmação ou de registro.",
      "impact": "implementation-detail",
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
    "rationale": "A confirmação é obrigatória antes da conclusão; o critério não estabelece que ela seja suficiente para concluir.",
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
    "sha256": "a353a0d5fe18876d845c55dffa4bfce4b59bdc180e58515a94c089577db17dd7"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Melhorar o processo de publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "As etapas, os papéis e as condições de conclusão foram declarados indefinidos.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "dafacec9c3ffc497aacf6e660a88e72985ea402d88747cab1e55de1f549622d7"
  },
  {
    "id": "context-2",
    "kind": "statement",
    "text": "Autores.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Público explicitamente indicado.",
    "source_atom_ids": [
      "atom-2"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "a146674e264a73ced2e9690c0eefee59e7e90fb559dcd077867586a0f62a4e5e"
  },
  {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano são princípios do projeto.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Esses princípios não estabelecem permissões ou aprovações adicionais.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "4efeeaaa821127ee4be5f0a23a9b4b56a65ef112c91f97dc26b32858b24662bb"
  },
  {
    "id": "context-4",
    "kind": "statement",
    "text": "Organizar a publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades declaradas em termos amplos.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "b9b86870b5cff96c31edb18c5f61deb92f0a95b1a6a8b0bdbf2e62e99a1b8fa6"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A aplicabilidade não foi especificada. A obrigação é preservada sem atribuir um gatilho, equiparar o responsável ao operador ou estabelecer uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "85c801107ab455684f50114f7bbdf52c4243367fff8e3451d705771759df7287"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de build é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite explícito de custo.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "3b21eeb4753911a83332d2167e45e75ee78131a01e115ea3404e696f4bddf758"
  },
  {
    "id": "issue-1",
    "kind": "question",
    "text": "Quais condições determinam a conclusão do processo de publicação da equipe, além da confirmação obrigatória pelo operador?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "outcome",
    "rationale": "As condições de conclusão estão explicitamente indefinidas. A confirmação estabelece uma obrigação prévia, mas não determina quando o processo pode ser considerado concluído.",
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
    "sha256": "02abb96df04d1a3b5fb040fbac72df48df7012afe1d6ace8f504be5d9d1e5c55"
  },
  {
    "id": "issue-2",
    "kind": "question",
    "text": "Quais etapas e papéis devem compor o processo de organização da publicação e registro de decisões?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "implementation-detail",
    "rationale": "Etapas e papéis foram declarados indefinidos; seu detalhamento auxilia a implementação, sem alterar por si só a obrigação conhecida de confirmação ou de registro.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "59af39c53c5d5514030a470f5758fa57e96a5b20116869538e451fac7f83faec"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "7e552b1881ef697bac14441cb3002defeb5899125cb706fba093edfc3100709f",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "a353a0d5fe18876d845c55dffa4bfce4b59bdc180e58515a94c089577db17dd7",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige confirmação pelo operador antes da conclusão, sem torná-la suficiente."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "dafacec9c3ffc497aacf6e660a88e72985ea402d88747cab1e55de1f549622d7",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes expressam melhoria do processo, publicação da equipe e registro de decisões."
    },
    {
      "finding_id": "context-2",
      "finding_sha256": "a146674e264a73ced2e9690c0eefee59e7e90fb559dcd077867586a0f62a4e5e",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O público indicado é autores."
    },
    {
      "finding_id": "context-3",
      "finding_sha256": "4efeeaaa821127ee4be5f0a23a9b4b56a65ef112c91f97dc26b32858b24662bb",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os dois princípios estão expressos; não conferem autorização."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "b9b86870b5cff96c31edb18c5f61deb92f0a95b1a6a8b0bdbf2e62e99a1b8fa6",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Reproduz as capacidades declaradas."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "85c801107ab455684f50114f7bbdf52c4243367fff8e3451d705771759df7287",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável, sem definir aplicabilidade ou equipará-lo ao operador."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "3b21eeb4753911a83332d2167e45e75ee78131a01e115ea3404e696f4bddf758",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo de custo máximo em USD contém 0.0."
    },
    {
      "finding_id": "issue-1",
      "finding_sha256": "02abb96df04d1a3b5fb040fbac72df48df7012afe1d6ace8f504be5d9d1e5c55",
      "source_atom_ids": [
        "atom-1",
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "As condições de conclusão estão indefinidas; a confirmação prévia não estabelece suficiência."
    },
    {
      "finding_id": "issue-2",
      "finding_sha256": "59af39c53c5d5514030a470f5758fa57e96a5b20116869538e451fac7f83faec",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "inappropriate",
      "note": "Etapas e papéis estão indefinidos, mas a pergunta genérica não identifica mudança de regra, autorização, resultado ou precedência."
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
      "note": "A fonte situa a obrigação antes de concluir."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A fonte atribui ao operador a confirmação da publicação da equipe."
    }
  ],
  "omissions": [
    {
      "id": "omission-1",
      "kind": "question",
      "text": "Em quais situações é obrigatório registrar a identidade e quem deve ser identificado como responsável?",
      "rationale": "A restrição não define sua aplicabilidade nem o responsável. Essas respostas determinam quando e de quem o registro é exigido; não se pode presumir que seja o operador.",
      "source_atom_ids": [
        "atom-5"
      ],
      "impact": "rule"
    }
  ],
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
      "note": "Melhoria e indefinições estão representadas."
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
      "note": "Princípio preservado."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "a6e3b461d6bc6975496196edb2b7d4ea96130a66c49e4e058c4d66078d23422f",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Princípio preservado sem inferir aprovação."
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
      "note": "Obrigação preservada; falta pergunta material sobre aplicabilidade e identidade do responsável."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
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
        "context-4",
        "issue-1",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Capacidades representadas; todas as citações mantidas."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "c52f9dd3da88167ffe7a9e1bf99a6efa142a0bb83392caacb04c20e3d767b055",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "issue-1"
      ],
      "omission_ids": [],
      "note": "Confirmação prévia preservada sem inferir autorização suficiente para concluir."
    }
  ]
}
```

## Julgamentos pendentes

Os seis critérios e inventários de suporte/cobertura precisam de decisão humana explícita. O aceite da referência histórica não é transferido para uma análise diferente. Compilação não autorizada; modelo não qualificado.
