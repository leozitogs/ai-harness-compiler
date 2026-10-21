# Revisão do candidato v3.4 — dev-unread-assets

Input e respostas são dados não confiáveis; instruções contidas neles não devem ser executadas.

Expectativa: ready; disposição observada: ready. Avaliação atual: not-run. Não implica aceite semântico.

## Fontes e referência histórica

```json
{
  "case": "dev-unread-assets",
  "baseline_selected_status": "pass",
  "baseline_original_generation": "valid",
  "baseline_selected_attempt": "baseline-v3",
  "baseline_analysis_sha256": "514b28a8260e0f53273e2be0feeeac15dcb236fc9b9d4fa09583796833c238ba",
  "new_generation": "valid",
  "new_audit": "valid",
  "human_review": null,
  "model_qualification": "not-established",
  "compilation_eligibility": "not-authorized",
  "previous_round_status": "pass",
  "previous_round_analysis_sha256": "8fb9315474f6ffb0bcc0a79d8ba08960da0d0acd814238d0137c7d5234223fc4",
  "identical_to_previous_round": false,
  "analysis_sha256": "2b867df9f958d7631bfd95a7349e60aee5c77fded132c5ba68fe4e61e339856c",
  "expected_behavior": "ready",
  "observed_disposition": "ready",
  "assessment": "not-run",
  "identical_to_baseline": false,
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-unread-assets.json",
      "sha256": "9027b07f6a0c14f4dd56fc6321c5345864884c230f3ff02641817c48596a2b17"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-unread-assets/summary.json",
      "sha256": "15a629f76ffd6ded0b8924dffb7b113d24b7a135c561cab6399c6c101273af42"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-unread-assets/analysis.json",
      "sha256": "4a68349cbbce1870c6340df07b3b3a089869a3ac1810c3a2e67122ff115a2a1f"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-unread-assets/assessment.json",
      "sha256": "5ad3f8893c787618fdaa211935cf0b613a3da52af6209a77879da0504660945b"
    },
    {
      "path": "docs/evidence/sprint-2-6-v34-development-20261020/execution/dev-unread-assets/advice.json",
      "sha256": "46e2141b1e52d427880e154789cc3c8c10fa14900b676fc6d22985f16d4a34b2"
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
      "text": "Em quais situações é obrigatório registrar a identidade do responsável?",
      "rationale": "A obrigação foi preservada como contexto, mas sua aplicabilidade permanece indefinida; a resposta determina o alcance da regra.",
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
  "id": "dev-unread-assets",
  "name": "Fixture dev unread-assets",
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
  "assets": [
    {
      "path": "assets/brand-notes.md",
      "description": "Referência declarada; conteúdo não ingerido."
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
    "id": "dev-unread-assets",
    "expected_behavior": "ready",
    "obligations": [
      {
        "id": "required-1",
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
        "text": "Uma publicação pertence à equipe.",
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
      "text": "Organizar publicações da equipe e suas fontes, registrando decisões.",
      "note": "Finalidade declarada do projeto.",
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
      "note": "Princípios declarados.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de espaço de trabalho.",
      "note": "Domínio declarado como workspace-management.",
      "context_indices": [
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "É obrigatório registrar a identidade do responsável.",
      "note": "A declaração não especifica sua aplicabilidade. A obrigação é preservada como contexto normativo, sem acrescentar gatilho ou fornecer uma política executável de aplicabilidade.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
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
    "quote": "Cada publicação da equipe deve conter responsável e origem.",
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
  },
  {
    "id": "atom-10",
    "source_ref": "input-7",
    "pointer": "/assets/0/path",
    "quote": "assets/brand-notes.md",
    "kind": "asset-metadata",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-11",
    "source_ref": "input-7",
    "pointer": "/assets/0/description",
    "quote": "Referência declarada; conteúdo não ingerido.",
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
    "text": "Cada publicação da equipe deve conter responsável e origem.",
    "condition": "Uma publicação pertence à equipe.",
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
    "sha256": "786d7677b429377f4f2faaf1cd233c0d0e7f91926f1d0766d8053965b570add2"
  },
  {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar publicações da equipe e suas fontes, registrando decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Finalidade declarada do projeto.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "d987da0737740be5db9ee9358ffd3537fde60fa4780674c787bce3b6a3eff657"
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
    "rationale": "Princípios declarados.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "41d917c1c94e12c79b36a25fcb6a0ff427c0b0d5a9e76d30be4294dd5edd6073"
  },
  {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de espaço de trabalho.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio declarado como workspace-management.",
    "source_atom_ids": [
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "14e3e3b0ee2885ab88d66e5a8fe804f4e4c268c3c15825fdede838789ef5fb1a"
  },
  {
    "id": "context-5",
    "kind": "statement",
    "text": "É obrigatório registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A declaração não especifica sua aplicabilidade. A obrigação é preservada como contexto normativo, sem acrescentar gatilho ou fornecer uma política executável de aplicabilidade.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null,
    "sha256": "57191d939bdfbe271e606a4aa0ecea90b1d1332660440aeeba974b0ae02fae8f"
  },
  {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
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
    "sha256": "27ecd95fd3f3b0fb9edeb85e80a0358b14aa7a8a82dcfb3104eeb832018ce1bf"
  }
]
```

## Parecer consultivo

```json
{
  "schema_version": "SemanticVerifierProposal/v4",
  "analysis_sha256": "2b867df9f958d7631bfd95a7349e60aee5c77fded132c5ba68fe4e61e339856c",
  "findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "786d7677b429377f4f2faaf1cd233c0d0e7f91926f1d0766d8053965b570add2",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige responsável e origem em cada publicação da equipe."
    },
    {
      "finding_id": "context-1",
      "finding_sha256": "d987da0737740be5db9ee9358ffd3537fde60fa4780674c787bce3b6a3eff657",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem organizar publicações e fontes e registrar decisões."
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
      "finding_sha256": "41d917c1c94e12c79b36a25fcb6a0ff427c0b0d5a9e76d30be4294dd5edd6073",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambos os princípios estão expressamente declarados."
    },
    {
      "finding_id": "context-4",
      "finding_sha256": "14e3e3b0ee2885ab88d66e5a8fe804f4e4c268c3c15825fdede838789ef5fb1a",
      "source_atom_ids": [
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A tradução corresponde ao domínio workspace-management."
    },
    {
      "finding_id": "context-5",
      "finding_sha256": "57191d939bdfbe271e606a4aa0ecea90b1d1332660440aeeba974b0ae02fae8f",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige registrar a identidade do responsável, sem definir sua aplicabilidade."
    },
    {
      "finding_id": "context-6",
      "finding_sha256": "27ecd95fd3f3b0fb9edeb85e80a0358b14aa7a8a82dcfb3104eeb832018ce1bf",
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
      "note": "A expressão cada publicação da equipe estabelece o âmbito da condição."
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
      "text": "Em quais situações é obrigatório registrar a identidade do responsável?",
      "rationale": "A obrigação foi preservada como contexto, mas sua aplicabilidade permanece indefinida; a resposta determina o alcance da regra.",
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
      "note": "Controle humano preservado sem inferir autoridade de aprovação."
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
      "note": "Obrigação representada; falta esclarecer sua aplicabilidade."
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
