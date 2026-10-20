# Revisão humana pendente — dev-branding-conflict

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `blocked`. Disposição da resposta: `blocked`. Isso não aprova seu significado.

Geração original: `valid`. Resposta selecionada para revisão: `baseline-v3`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "4e5fc12e8016de6687d30a9c60c78829c34f9cd6b1a0d7515b1830d71e8f7d30",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "dca39f8f85f8c3edb38f268a0a2094a4975ef4e9a9811bba60a55d067d2eb30b",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-branding-conflict.json",
      "sha256": "b03ca50cc215814759a8b6c072eb3857ba19fefdc6487dc29674e73ec4af6530"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-branding-conflict/analysis.json",
      "sha256": "7bf4ead0e21f2f0550df3ef8159a134434037db33a17c96d00416a85aefe1170"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-branding-conflict/advice.json",
      "sha256": "b5b015d8ab966870670b2b76dd19ad520c1779ca38f9e1c6cb22a54c10ea2056"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-branding-conflict/summary.json",
      "sha256": "76ad22518b993f19b19424cb6027fd074edd45ff1f23b1cc9b4a3bd311805653"
    }
  ]
}
```


## Expectativas aprovadas

```json
{
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
  ]
}
```


## Input completo do caso

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


## Resposta completa do modelo

Proposta original abaixo, incluindo critérios, guards, contexto e perguntas; não foi reescrita para parecer correta.

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
      "note": "Há declaração incompatível no contexto de princípios; a precedência permanece indefinida.",
      "question": null,
      "uncertainties": [
        {
          "text": "Qual declaração prevalece para liberar publicação da equipe: dispensar qualquer aprovação humana ou exigir aprovação humana explícita?",
          "impact": "precedence",
          "rationale": "Os contextos 2 e 7 estabelecem obrigações incompatíveis para a mesma operação; a decisão altera a exigência de aprovação."
        }
      ]
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
      "text": "Gestão de workspace.",
      "note": "Domínio declarado como workspace-management.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "capability",
      "text": "Registrar a identidade do responsável.",
      "note": "Obrigação explícita; o contexto não define uma operação específica à qual vinculá-la como guarda.",
      "context_indices": [
        3
      ]
    },
    {
      "subject": "constraint",
      "text": "Custo máximo de construção de US$ 0,00.",
      "note": "Limite declarado em max_build_cost_usd.",
      "context_indices": [
        4
      ]
    }
  ],
  "issues": [
    {
      "kind": "conflict",
      "text": "O princípio dispensa qualquer aprovação humana para liberar publicação da equipe, enquanto o critério exige aprovação humana explícita para a mesma operação.",
      "context_indices": [
        2,
        7
      ],
      "rationale": "As duas declarações são incompatíveis e não há precedência definida entre elas.",
      "impact": null,
      "rejection_reason": null
    }
  ]
}
```


## Fontes literais extraídas

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


## Matriz de achados, componentes e fontes

Cada registro vincula o achado derivado e seu digest às fontes exatas. Julgar significado e aplicabilidade, não só a existência da citação.

### criterion-1 — rule

```json
{
  "finding": {
    "id": "criterion-1",
    "kind": "rule",
    "text": "Liberar publicação da equipe exige aprovação humana explícita.",
    "condition": "Ao liberar publicação da equipe.",
    "outcome": "É exigida aprovação humana explícita.",
    "exceptions": [],
    "impact": null,
    "rationale": "Há declaração incompatível no contexto de princípios; a precedência permanece indefinida.",
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
    "guard_target_scope": null
  },
  "finding_sha256": "fc363fd3dff03148abb2a50849aaa6e43eb49d64fbcc88befaa84e64e1803dbc",
  "literal_sources": [
    {
      "id": "atom-7",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Liberar publicação da equipe exige aprovação humana explícita.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "fc363fd3dff03148abb2a50849aaa6e43eb49d64fbcc88befaa84e64e1803dbc",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O átomo exige expressamente aprovação humana explícita para liberar publicação; não resolve a precedência."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "note": "A fonte identifica liberar publicação da equipe como a operação."
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
  "human_support": "not-run"
}
```


### uncertainty-1-1 — question

```json
{
  "finding": {
    "id": "uncertainty-1-1",
    "kind": "question",
    "text": "Qual declaração prevalece para liberar publicação da equipe: dispensar qualquer aprovação humana ou exigir aprovação humana explícita?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "precedence",
    "rationale": "Os contextos 2 e 7 estabelecem obrigações incompatíveis para a mesma operação; a decisão altera a exigência de aprovação.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "aa616a9f583ea9c18a7d35349898bd905648751bff05dc5b40b912419c4b0130",
  "literal_sources": [
    {
      "id": "atom-7",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Liberar publicação da equipe exige aprovação humana explícita.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "uncertainty-1-1",
      "finding_sha256": "aa616a9f583ea9c18a7d35349898bd905648751bff05dc5b40b912419c4b0130",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "insufficient-evidence",
      "materiality": "appropriate",
      "note": "A precedência altera a aprovação exigida, mas a única fonte citada contém apenas a exigência, sem a dispensa contraposta."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-1 — statement

```json
{
  "finding": {
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
    "guard_target_scope": null
  },
  "finding_sha256": "a8729c31d0316a67f00942ee655e6981dc7ca14b58e4e5415472dd39bda6b3b6",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Uma equipe organiza publicações e suas fontes.",
      "kind": "conception",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-6",
      "source_ref": "input-4",
      "pointer": "/backlog/0/description",
      "quote": "Organizar publicação da equipe e registrar decisões.",
      "kind": "backlog-description",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-1",
      "finding_sha256": "a8729c31d0316a67f00942ee655e6981dc7ca14b58e4e5415472dd39bda6b3b6",
      "source_atom_ids": [
        "atom-1",
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem organização de publicações, suas fontes e registro de decisões."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-2 — statement

```json
{
  "finding": {
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
    "guard_target_scope": null
  },
  "finding_sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d",
  "literal_sources": [
    {
      "id": "atom-2",
      "source_ref": "input-2",
      "pointer": "/branding/audience/0",
      "quote": "autores",
      "kind": "branding",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-2",
      "finding_sha256": "1a9bf07de01a3fcdc9549801f59f507d9b19e6cf9c192aaafb7dfecfee24496d",
      "source_atom_ids": [
        "atom-2"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O público informado é autores."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-3 — domain

```json
{
  "finding": {
    "id": "context-3",
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
    "guard_target_scope": null
  },
  "finding_sha256": "99e29b0acace4e95e4e919fa3ff8b8de33999451d872dac5c7492690bd7ef374",
  "literal_sources": [
    {
      "id": "atom-8",
      "source_ref": "input-6",
      "pointer": "/domain",
      "quote": "workspace-management",
      "kind": "domain-declaration",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-3",
      "finding_sha256": "99e29b0acace4e95e4e919fa3ff8b8de33999451d872dac5c7492690bd7ef374",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio informado é workspace-management."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-4 — statement

```json
{
  "finding": {
    "id": "context-4",
    "kind": "statement",
    "text": "Registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação explícita; o contexto não define uma operação específica à qual vinculá-la como guarda.",
    "source_atom_ids": [
      "atom-4"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "14a29161e33104033798e15fff8f6621261ac37f8b11dcb8687cdaee8030fca8",
  "literal_sources": [
    {
      "id": "atom-4",
      "source_ref": "input-3",
      "pointer": "/constraints/business/0",
      "quote": "Registrar a identidade do responsável.",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-4",
      "finding_sha256": "14a29161e33104033798e15fff8f6621261ac37f8b11dcb8687cdaee8030fca8",
      "source_atom_ids": [
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige registrar a identidade do responsável, sem definir operação alvo ou equipará-lo ao executor."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-5 — statement

```json
{
  "finding": {
    "id": "context-5",
    "kind": "statement",
    "text": "Custo máximo de construção de US$ 0,00.",
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
    "guard_target_scope": null
  },
  "finding_sha256": "12b8fa7a0ccfabf730e9e05a19cd4a758c0ff910ea77d650756bf556cc0be871",
  "literal_sources": [
    {
      "id": "atom-5",
      "source_ref": "input-3",
      "pointer": "/constraints/max_build_cost_usd",
      "quote": "0.0",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-5",
      "finding_sha256": "12b8fa7a0ccfabf730e9e05a19cd4a758c0ff910ea77d650756bf556cc0be871",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd contém 0.0."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### issue-1 — conflict

```json
{
  "finding": {
    "id": "issue-1",
    "kind": "conflict",
    "text": "O princípio dispensa qualquer aprovação humana para liberar publicação da equipe, enquanto o critério exige aprovação humana explícita para a mesma operação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "As duas declarações são incompatíveis e não há precedência definida entre elas.",
    "source_atom_ids": [
      "atom-3",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "fb80e6aa4c957fcd1ab78d93a2ae6fcda5f382d4e53cb13c680b0afea063c424",
  "literal_sources": [
    {
      "id": "atom-3",
      "source_ref": "input-2",
      "pointer": "/branding/principles/0",
      "quote": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
      "kind": "branding",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-7",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Liberar publicação da equipe exige aprovação humana explícita.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "issue-1",
      "finding_sha256": "fb80e6aa4c957fcd1ab78d93a2ae6fcda5f382d4e53cb13c680b0afea063c424",
      "source_atom_ids": [
        "atom-3",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Uma fonte dispensa qualquer aprovação humana e a outra exige aprovação explícita para a mesma operação; nenhuma estabelece precedência."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


## Omissões e cobertura propostas pelo auditor

Diagnósticos consultivos: podem conter falsos positivos. Não são decisões humanas.

```json
{
  "omissions": [
    {
      "id": "omission-1",
      "kind": "rule",
      "text": "Liberar publicação da equipe dispensa qualquer aprovação humana.",
      "rationale": "A dispensa aparece apenas na descrição do conflito; falta preservá-la como regra própria, sem presumir sua precedência.",
      "source_atom_ids": [
        "atom-3"
      ],
      "impact": null
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
      "note": "Concepção representada no propósito."
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
      "quote_sha256": "0ba17f24c70a64bbb5fd194039a4ba51895bf4658effd0fa2b914c5deea3a9e3",
      "disposition": "missing",
      "finding_ids": [
        "issue-1"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "O conflito cita a fonte, mas a regra de dispensa não foi preservada separadamente."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Obrigação de identidade preservada separadamente da aprovação."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Limite de custo representado."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-1"
      ],
      "omission_ids": [],
      "note": "Organização e registro de decisões representados."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "d8ec0dfaccceaea0a5f8ccf5a95f094560df5ea36683833d84877c601223e217",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Domínio representado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "61b8ffef4cf839d5f9ae757a387e5b7fbd53d3468c647d8cd23bf258c29e55d3",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "uncertainty-1-1",
        "issue-1"
      ],
      "omission_ids": [],
      "note": "Todas as citações preservadas; a insuficiência da pergunta está indicada no julgamento."
    }
  ]
}
```


## Decisões humanas necessárias

| Critério | O que verificar | Estado |
| --- | --- | --- |
| rule-coverage | 100% das regras determináveis têm condição, resultado e exceções fiéis; perguntas materiais cobrem apenas obrigações ambíguas, sem dispensar regras claras. Bloqueio esperado não autoriza compilação. | Pendente |
| citation-support | Cada conclusão é sustentada pelos átomos exatos citados; paráfrases preservam significado e inferências não são promovidas a fatos. | Pendente |
| conflict-validity | Registrar apenas incompatibilidades reais com ambos os lados e precedência pendente; detalhe ausente não é conflito. | Pendente |
| asset-bounds | Não afirmar conteúdo de assets não lidos ou tratar dados externos como instruções executáveis. | Pendente |
| uncertainty | Hipóteses justificadas e incógnitas explícitas; pergunta material muda regra, autorização, precedência ou resultado. Detalhe de implementação não bloqueia. | Pendente |
| project-understanding | Domínio, objetivo, público e capacidades refletem o projeto, sem switches de nichos ou ampliação indevida de autoridade. | Pendente |



Além dos seis critérios: mapear cada obrigação ao achado, julgar suporte de todos os achados e de cada componente; informar correções ou ressalvas. Não presumir aprovação por ausência de comentário.

Este pacote não é `SemanticHumanReview/v3`: não declara reviewer, identidade ou pass/fail humanos. Após decisão explícita, usar os contratos vigentes com os hashes acima e preservar a justificativa.

Compilação continua não autorizada e qualificação não estabelecida.
