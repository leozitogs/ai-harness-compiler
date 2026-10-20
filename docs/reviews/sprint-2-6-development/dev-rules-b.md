# Revisão humana pendente — dev-rules-b

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `ready`. Disposição da resposta: `ready`. Isso não aprova seu significado.

Geração original: `valid`. Resposta selecionada para revisão: `baseline-v3`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "9d7354f306a8e7b52957c87187eab0d05c1a66f66ef2c2ddf78b8f858d196b58",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "37259cfadefec1d810777fb46d24278122889ce8e2703457e2518d39ffee6231",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-rules-b.json",
      "sha256": "9e516037eefd452f56323845d4aa5adc613a713d34b77da788c5629eaf131fa0"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-rules-b/analysis.json",
      "sha256": "56ed52e69d22d0e3a95eaa07c31986550360813cff9bee444845ac4e6406b905"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-rules-b/advice.json",
      "sha256": "320d60565bb66c35b7251097e364ff002c630f35c0555525523eadf5c6b423fd"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-rules-b/summary.json",
      "sha256": "0c6802f79372271a788a427c76d3f97ca1edc5b60a4413eb930a2dc0fc3a79f0"
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
      "quote": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
      "disposition": "rule"
    }
  ],
  "requires_conflict": false,
  "conflict_source_pointers": []
}
```


## Input completo do caso

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


## Resposta completa do modelo

Proposta original abaixo, incluindo critérios, guards, contexto e perguntas; não foi reescrita para parecer correta.

```json
{
  "schema_version": "SemanticAnalysisProposal/v3",
  "criteria": [
    {
      "source_atom_id": "atom-8",
      "kind": "business-rule",
      "condition": {
        "text": "O autor deseja liberar uma publicação da equipe.",
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
      "note": "A autorização não depende de aprovação de terceiros.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [
    {
      "id": "guard-1",
      "condition": {
        "text": "O autor libera uma publicação da equipe.",
        "source_atom_ids": [
          "atom-8"
        ]
      },
      "effect": {
        "text": "Registrar a identidade do responsável.",
        "source_atom_ids": [
          "atom-5"
        ]
      },
      "target_scope": "criteria",
      "target_criterion_atom_ids": [
        "atom-8"
      ],
      "note": "A obrigação de identificação acompanha a liberação sem exigir aprovação de terceiros."
    }
  ],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar publicações da equipe, suas fontes e o registro de decisões.",
      "note": "Finalidade expressa na concepção e na descrição do backlog.",
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
      "note": "Princípios declarados, compatíveis com a liberação pelo autor e o registro do responsável.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de espaço de trabalho, com organização de publicações e fontes.",
      "note": "Domínio declarado e contextualizado pela concepção.",
      "context_indices": [
        0,
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é de US$ 0,00.",
      "note": "Limite financeiro explícito.",
      "context_indices": [
        5
      ]
    }
  ],
  "issues": []
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


## Matriz de achados, componentes e fontes

Cada registro vincula o achado derivado e seu digest às fontes exatas. Julgar significado e aplicabilidade, não só a existência da citação.

### criterion-1 — rule

```json
{
  "finding": {
    "id": "criterion-1",
    "kind": "rule",
    "text": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
    "condition": "O autor deseja liberar uma publicação da equipe.",
    "outcome": "O autor pode liberar a publicação sem aprovação de terceiros.",
    "exceptions": [],
    "impact": null,
    "rationale": "A autorização não depende de aprovação de terceiros.",
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
    "guard_target_scope": null
  },
  "finding_sha256": "0f2d267cdb549ec08cef5f6935430207b66f1b6928ebd8ced9973b6021ce530b",
  "literal_sources": [
    {
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "0f2d267cdb549ec08cef5f6935430207b66f1b6928ebd8ced9973b6021ce530b",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte permite expressamente ao autor liberar a publicação sem aprovação de terceiros."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A permissão expressa contempla o autor que deseja liberar uma publicação da equipe."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A fonte declara a liberação pelo autor sem aprovação de terceiros."
    }
  ],
  "human_support": "not-run"
}
```


### guard-1 — rule

```json
{
  "finding": {
    "id": "guard-1",
    "kind": "rule",
    "text": "Registrar a identidade do responsável.",
    "condition": "O autor libera uma publicação da equipe.",
    "outcome": "Registrar a identidade do responsável.",
    "exceptions": [],
    "impact": null,
    "rationale": "A obrigação de identificação acompanha a liberação sem exigir aprovação de terceiros.",
    "source_atom_ids": [
      "atom-8",
      "atom-5"
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
          "atom-5"
        ]
      }
    ],
    "guard_target_atom_ids": [
      "atom-8"
    ],
    "guard_target_scope": "criteria"
  },
  "finding_sha256": "a853ea90ae31cf7416b075486072fd99db7c6679ca89bde0882b105db90b74cd",
  "literal_sources": [
    {
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "O autor pode liberar publicação da equipe sem aprovação de terceiros.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-5",
      "source_ref": "input-3",
      "pointer": "/constraints/business/0",
      "quote": "Registrar a identidade do responsável.",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "guard-1",
      "finding_sha256": "a853ea90ae31cf7416b075486072fd99db7c6679ca89bde0882b105db90b74cd",
      "source_atom_ids": [
        "atom-8",
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A liberação pelo autor é prevista em atom-8; atom-5 exige registrar a identidade do responsável. Isso não estabelece que o responsável seja o autor ou o executor."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "guard-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A liberação de publicação da equipe pelo autor é a ação expressamente prevista."
    },
    {
      "finding_id": "guard-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "note": "A fonte exige literalmente registrar a identidade do responsável, sem definir quem ocupa esse papel."
    }
  ],
  "human_support": "not-run"
}
```


### context-1 — statement

```json
{
  "finding": {
    "id": "context-1",
    "kind": "statement",
    "text": "Organizar publicações da equipe, suas fontes e o registro de decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Finalidade expressa na concepção e na descrição do backlog.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "08e91a55aae4a17ce9282c98a1e5334729ee9eb4d7c978cf98c794df2d60900d",
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
      "id": "atom-7",
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
      "finding_sha256": "08e91a55aae4a17ce9282c98a1e5334729ee9eb4d7c978cf98c794df2d60900d",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem organizar publicações e fontes e registrar decisões."
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
      "note": "O público declarado é autores."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-3 — statement

```json
{
  "finding": {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Princípios declarados, compatíveis com a liberação pelo autor e o registro do responsável.",
    "source_atom_ids": [
      "atom-3",
      "atom-4"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "8a15dd59cbc86afbc2bb79a0e64a1b0a5f7a51e1704ccacce8e682998117c95a",
  "literal_sources": [
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
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-3",
      "finding_sha256": "8a15dd59cbc86afbc2bb79a0e64a1b0a5f7a51e1704ccacce8e682998117c95a",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram rastreabilidade e controle humano, sem especificar aprovação por terceiros."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-4 — domain

```json
{
  "finding": {
    "id": "context-4",
    "kind": "domain",
    "text": "Gestão de espaço de trabalho, com organização de publicações e fontes.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio declarado e contextualizado pela concepção.",
    "source_atom_ids": [
      "atom-1",
      "atom-9"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "be9f664fe999dee7e7774748e40fefe51f97bb11b5efaa227661fba7d933561f",
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
      "id": "atom-9",
      "source_ref": "input-6",
      "pointer": "/domain",
      "quote": "workspace-management",
      "kind": "domain-declaration",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-4",
      "finding_sha256": "be9f664fe999dee7e7774748e40fefe51f97bb11b5efaa227661fba7d933561f",
      "source_atom_ids": [
        "atom-1",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O domínio declarado é gestão de espaço de trabalho; a concepção inclui publicações e fontes."
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
    "text": "O custo máximo de construção é de US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite financeiro explícito.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "f32deeeb187eed27af4de7189d53994a520a442e0aa1bc807fbc837848cb0e2e",
  "literal_sources": [
    {
      "id": "atom-6",
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
      "finding_sha256": "f32deeeb187eed27af4de7189d53994a520a442e0aa1bc807fbc837848cb0e2e",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd tem valor 0.0."
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
      "kind": "question",
      "text": "Quem deve ser identificado como responsável para cumprir a exigência de registro?",
      "rationale": "A exigência não define o responsável. A resposta determina de quem deve ser registrada a identidade; não se pode presumir que seja o autor ou o executor autenticado.",
      "source_atom_ids": [
        "atom-5"
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
      "note": "Controle humano representado; não exige por si só aprovação de terceiros."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "missing",
      "finding_ids": [
        "guard-1"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Obrigação representada; falta esclarecer quem deve ser identificado como responsável."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Limite financeiro representado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "context-1"
      ],
      "omission_ids": [],
      "note": "Organização da publicação e registro de decisões representados."
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
        "criterion-1",
        "guard-1"
      ],
      "omission_ids": [],
      "note": "Permissão e condição da guarda representadas; a fonte não identifica o responsável exigido pela guarda."
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
