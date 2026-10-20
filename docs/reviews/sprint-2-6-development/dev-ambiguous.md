# Revisão humana pendente — dev-ambiguous

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `blocked`. Disposição da resposta: `blocked`. Isso não aprova seu significado.

Geração original: `valid`. Resposta selecionada para revisão: `baseline-v3`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "96d9954a55ca4bf3aa2ad1d8156c160c4692b97b3d1cdcd51c2f84adbf8ccd48",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "44f9c5bbb4d4461109433ede9bddcbb99b27131c08af8714d6fd314fd86adc54",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-ambiguous.json",
      "sha256": "b4b91de66473ba2ce628faae3aefddc571213af16ae08a34c00ef2f2440df3ae"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-ambiguous/analysis.json",
      "sha256": "a5c9bed24fc0e21a8b2ae2cb01bb7b881eeb9340150532b48935356d57c80468"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-ambiguous/advice.json",
      "sha256": "3b60db0dbaf855a7ca7cfcce67318fa84120e3665d81608ead50477d196cd5ee"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-ambiguous/summary.json",
      "sha256": "2610e1c8452ea781335ff8d1ffae21ea44934ad68170f4607d986b37caf2ed18"
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
  "conflict_source_pointers": []
}
```


## Input completo do caso

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
        "text": "Antes de concluir a publicação da equipe.",
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
      "note": "A confirmação é uma condição necessária para concluir; as demais condições de conclusão não estão definidas.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [
    {
      "id": "guard-1",
      "condition": {
        "text": "Ao registrar decisões no processo de publicação da equipe.",
        "source_atom_ids": [
          "atom-7"
        ]
      },
      "effect": {
        "text": "Registrar a identidade do responsável.",
        "source_atom_ids": [
          "atom-5"
        ]
      },
      "target_scope": "project",
      "target_criterion_atom_ids": [],
      "note": "Exigência de rastreabilidade; não concede autorização para publicar ou concluir."
    }
  ],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Melhorar a organização da publicação da equipe e registrar decisões.",
      "note": "O processo ainda carece de definições operacionais.",
      "context_indices": [
        0,
        6
      ]
    },
    {
      "subject": "audience",
      "text": "Autores.",
      "note": "Público explicitamente declarado.",
      "context_indices": [
        1
      ]
    },
    {
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano orientam o projeto.",
      "note": "Princípios declarados.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Processo de publicação em equipe.",
      "note": "Não há indicação do tipo de conteúdo publicado.",
      "context_indices": [
        6,
        7
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar publicações da equipe e registrar decisões.",
      "note": "Capacidades de apoio declaradas em termos amplos.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite financeiro informado.",
      "context_indices": [
        5
      ]
    }
  ],
  "issues": [
    {
      "kind": "question",
      "text": "Além da confirmação do operador, quais condições determinam que o processo de publicação da equipe pode ser concluído?",
      "context_indices": [
        0,
        7
      ],
      "rationale": "As condições de conclusão estão explicitamente indefinidas. A confirmação conhecida permanece obrigatória, mas não estabelece sozinha quando a conclusão é válida.",
      "impact": "outcome",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Quais etapas compõem o processo de publicação da equipe?",
      "context_indices": [
        0,
        6
      ],
      "rationale": "As etapas estão explicitamente indefinidas; é necessário esclarecer quais atividades fazem parte do processo que deve ser organizado.",
      "impact": "rule",
      "rejection_reason": null
    },
    {
      "kind": "question",
      "text": "Como se distribuem os papéis e as responsabilidades no processo, incluindo quem pode atuar como operador e concluir a publicação?",
      "context_indices": [
        0,
        3,
        7
      ],
      "rationale": "Os papéis estão explicitamente indefinidos. A menção ao operador estabelece sua obrigação de confirmar, mas não determina quem pode exercer esse papel ou autorizar a conclusão.",
      "impact": "authorization",
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


## Matriz de achados, componentes e fontes

Cada registro vincula o achado derivado e seu digest às fontes exatas. Julgar significado e aplicabilidade, não só a existência da citação.

### criterion-1 — rule

```json
{
  "finding": {
    "id": "criterion-1",
    "kind": "rule",
    "text": "O operador confirma publicação da equipe antes de concluir.",
    "condition": "Antes de concluir a publicação da equipe.",
    "outcome": "O operador deve confirmar a publicação da equipe.",
    "exceptions": [],
    "impact": null,
    "rationale": "A confirmação é uma condição necessária para concluir; as demais condições de conclusão não estão definidas.",
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
  "finding_sha256": "f86cdc3b676314c69e97c03d4ee26ca8a0970107962abcce857e5f73b977d2f4",
  "literal_sources": [
    {
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "O operador confirma publicação da equipe antes de concluir.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "f86cdc3b676314c69e97c03d4ee26ca8a0970107962abcce857e5f73b977d2f4",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige confirmação pelo operador antes da conclusão."
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
      "note": "A expressão antes de concluir estabelece a condição temporal."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "A fonte atribui ao operador a confirmação da publicação."
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
    "condition": "Ao registrar decisões no processo de publicação da equipe.",
    "outcome": "Registrar a identidade do responsável.",
    "exceptions": [],
    "impact": null,
    "rationale": "Exigência de rastreabilidade; não concede autorização para publicar ou concluir.",
    "source_atom_ids": [
      "atom-7",
      "atom-5"
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
          "atom-5"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": "project"
  },
  "finding_sha256": "d0e87fb9a5d0fe1da38f7b9a9f97c42ad09c246e9028fc65dd9624c1b11f8a28",
  "literal_sources": [
    {
      "id": "atom-7",
      "source_ref": "input-4",
      "pointer": "/backlog/0/description",
      "quote": "Organizar publicação da equipe e registrar decisões.",
      "kind": "backlog-description",
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
      "finding_sha256": "d0e87fb9a5d0fe1da38f7b9a9f97c42ad09c246e9028fc65dd9624c1b11f8a28",
      "source_atom_ids": [
        "atom-7",
        "atom-5"
      ],
      "support": "insufficient-evidence",
      "materiality": "not-applicable",
      "note": "A obrigação de registrar a identidade é explícita, mas sua vinculação ao registro de decisões não está estabelecida pelas fontes dos componentes."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "guard-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "insufficient-evidence",
      "note": "A fonte prevê registrar decisões, mas não estabelece esse evento como condição de aplicação do registro de identidade."
    },
    {
      "finding_id": "guard-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "note": "A fonte exige literalmente registrar a identidade do responsável, sem identificar esse responsável."
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
    "text": "Melhorar a organização da publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "O processo ainda carece de definições operacionais.",
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
  "finding_sha256": "340c3255639a966f6d90d93ab2ef022dbc532e884a11ef5396e7d4242c98545d",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
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
      "finding_sha256": "340c3255639a966f6d90d93ab2ef022dbc532e884a11ef5396e7d4242c98545d",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram a melhoria do processo, a organização da publicação e o registro de decisões."
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
    "rationale": "Público explicitamente declarado.",
    "source_atom_ids": [
      "atom-2"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "21dc6c05c2a088cab8529fa0e078ade2a529107573d3220261170e6468056dd9",
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
      "finding_sha256": "21dc6c05c2a088cab8529fa0e078ade2a529107573d3220261170e6468056dd9",
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
    "text": "Rastreabilidade e controle humano orientam o projeto.",
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
    "guard_target_scope": null
  },
  "finding_sha256": "4c735e89c28f60cf50d508514af746bce5517f89e3a98b253993483af277f1a2",
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
      "finding_sha256": "4c735e89c28f60cf50d508514af746bce5517f89e3a98b253993483af277f1a2",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Rastreabilidade e controle humano constam como princípios."
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
    "text": "Processo de publicação em equipe.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Não há indicação do tipo de conteúdo publicado.",
    "source_atom_ids": [
      "atom-7",
      "atom-8"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "4a435d02417a6e89c3d7f6a0d8bf68c1d3d8ab3d0bfb47e1cbd1ba3fd36a0b6d",
  "literal_sources": [
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
  ],
  "advisory_findings": [
    {
      "finding_id": "context-4",
      "finding_sha256": "4a435d02417a6e89c3d7f6a0d8bf68c1d3d8ab3d0bfb47e1cbd1ba3fd36a0b6d",
      "source_atom_ids": [
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambas as fontes tratam da publicação da equipe."
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
    "text": "Organizar publicações da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades de apoio declaradas em termos amplos.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "fa9157944a8f7811ff1ea2d66703e5c2830c3e7971e4167481f658fcf7ef2f66",
  "literal_sources": [
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
      "finding_id": "context-5",
      "finding_sha256": "fa9157944a8f7811ff1ea2d66703e5c2830c3e7971e4167481f658fcf7ef2f66",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Organizar publicação e registrar decisões são capacidades expressas."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-6 — statement

```json
{
  "finding": {
    "id": "context-6",
    "kind": "statement",
    "text": "O custo máximo de construção é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite financeiro informado.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "979f0c11e0e076e9c133022e6952483189e1a3f4027ffa11b705c5193404db19",
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
      "finding_id": "context-6",
      "finding_sha256": "979f0c11e0e076e9c133022e6952483189e1a3f4027ffa11b705c5193404db19",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo de custo máximo de construção em dólares informa 0.0."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### issue-1 — question

```json
{
  "finding": {
    "id": "issue-1",
    "kind": "question",
    "text": "Além da confirmação do operador, quais condições determinam que o processo de publicação da equipe pode ser concluído?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "outcome",
    "rationale": "As condições de conclusão estão explicitamente indefinidas. A confirmação conhecida permanece obrigatória, mas não estabelece sozinha quando a conclusão é válida.",
    "source_atom_ids": [
      "atom-1",
      "atom-8"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "61044d20f272e0aed4b8859d39a0182288656ef5e4c7dfd6bf641593d9927b07",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
      "kind": "conception",
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
  ],
  "advisory_findings": [
    {
      "finding_id": "issue-1",
      "finding_sha256": "61044d20f272e0aed4b8859d39a0182288656ef5e4c7dfd6bf641593d9927b07",
      "source_atom_ids": [
        "atom-1",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "As condições de conclusão estão indefinidas; a confirmação explícita não determina sua suficiência."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### issue-2 — question

```json
{
  "finding": {
    "id": "issue-2",
    "kind": "question",
    "text": "Quais etapas compõem o processo de publicação da equipe?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "rule",
    "rationale": "As etapas estão explicitamente indefinidas; é necessário esclarecer quais atividades fazem parte do processo que deve ser organizado.",
    "source_atom_ids": [
      "atom-1",
      "atom-7"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "bf66afaf7f0d8220a30496c9d08abe849f4a504c949e67039fb45e73bc5321e4",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
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
      "finding_id": "issue-2",
      "finding_sha256": "bf66afaf7f0d8220a30496c9d08abe849f4a504c949e67039fb45e73bc5321e4",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "As etapas estão explicitamente indefinidas e determinam quais atividades integram o processo."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### issue-3 — question

```json
{
  "finding": {
    "id": "issue-3",
    "kind": "question",
    "text": "Como se distribuem os papéis e as responsabilidades no processo, incluindo quem pode atuar como operador e concluir a publicação?",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": "authorization",
    "rationale": "Os papéis estão explicitamente indefinidos. A menção ao operador estabelece sua obrigação de confirmar, mas não determina quem pode exercer esse papel ou autorizar a conclusão.",
    "source_atom_ids": [
      "atom-1",
      "atom-4",
      "atom-8"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "ae659c0009a4acd480ad7cc5eb46aa6deb4854d608a3037b2867229d938a1403",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Precisamos melhorar o processo; etapas, papéis e condições de conclusão não foram definidos.",
      "kind": "conception",
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
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "O operador confirma publicação da equipe antes de concluir.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "issue-3",
      "finding_sha256": "ae659c0009a4acd480ad7cc5eb46aa6deb4854d608a3037b2867229d938a1403",
      "source_atom_ids": [
        "atom-1",
        "atom-4",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "appropriate",
      "note": "Os papéis estão indefinidos; controle humano e confirmação pelo operador não identificam quem está autorizado a concluir."
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
  "omissions": [],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "12c881ea64cc68b9aaf7a45d4f29375b8d95498dbb4859448f7c857eb0f202c8",
      "disposition": "represented",
      "finding_ids": [
        "context-1",
        "issue-1",
        "issue-2",
        "issue-3"
      ],
      "omission_ids": [],
      "note": "A intenção de melhoria e as três indefinições estão contempladas."
    },
    {
      "atom_id": "atom-2",
      "quote_sha256": "75f26d13ebd8877644c57a369ce71b82b639903217ed12ebe61beeffd8c11586",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público contemplado."
    },
    {
      "atom_id": "atom-3",
      "quote_sha256": "e8a964e534bd9189a4c1ee68dc1e80429c5b14930ce7df548075257a8a8dccc7",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Princípio de rastreabilidade contemplado."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "a6e3b461d6bc6975496196edb2b7d4ea96130a66c49e4e058c4d66078d23422f",
      "disposition": "represented",
      "finding_ids": [
        "context-3",
        "issue-3"
      ],
      "omission_ids": [],
      "note": "Controle humano contemplado sem inferir autorização individual."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "represented",
      "finding_ids": [
        "guard-1"
      ],
      "omission_ids": [],
      "note": "A obrigação de identidade está registrada; a condição acrescentada foi julgada insuficientemente fundamentada."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Limite financeiro contemplado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "5f77f5215732224df6e88a779d30470fdd1c968ff4e40c54ff9fa444e009e034",
      "disposition": "represented",
      "finding_ids": [
        "guard-1",
        "context-1",
        "context-4",
        "context-5",
        "issue-2"
      ],
      "omission_ids": [],
      "note": "Organização e decisões contempladas; preservada a citação cuja ligação ao guard é incerta."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "c52f9dd3da88167ffe7a9e1bf99a6efa142a0bb83392caacb04c20e3d767b055",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "context-4",
        "issue-1",
        "issue-3"
      ],
      "omission_ids": [],
      "note": "Confirmação prévia contemplada, sem presumir suficiência ou autorização do operador."
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
