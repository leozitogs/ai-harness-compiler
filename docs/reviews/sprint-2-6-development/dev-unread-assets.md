# Revisão humana pendente — dev-unread-assets

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `ready`. Disposição da resposta: `ready`. Isso não aprova seu significado.

Geração original: `valid`. Resposta selecionada para revisão: `baseline-v3`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "3c63236be69375dd183ee04a12c9fe91be3b2a43a507b9c974db9ed5774f34c5",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "514b28a8260e0f53273e2be0feeeac15dcb236fc9b9d4fa09583796833c238ba",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-unread-assets.json",
      "sha256": "9027b07f6a0c14f4dd56fc6321c5345864884c230f3ff02641817c48596a2b17"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-unread-assets/analysis.json",
      "sha256": "365cbf5c8f47d8ab1b40775a254c1d408877e0ba8a53c141c93656069b76d954"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-unread-assets/advice.json",
      "sha256": "e848cb4c6fb26b432da7940a6d54cb4eedf78c5851efc407d5dfef5783d70147"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-unread-assets/summary.json",
      "sha256": "62c6d614feaf96bd39e92f71c46fbd65e69630ec50223b3ba86cbb045f0e0b9d"
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
      "quote": "Cada publicação da equipe deve conter responsável e origem.",
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
        "text": "Para cada publicação da equipe.",
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
      "note": "A identidade do responsável deve ser registrada, conforme a restrição de negócio.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar publicações da equipe, suas fontes e registrar decisões.",
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
      "text": "Rastreabilidade e controle humano.",
      "note": "Princípios declarados; não especificam etapas adicionais de aprovação.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "domain",
      "text": "Gestão de workspace aplicada à organização de publicações e fontes.",
      "note": "Interpretação da declaração de domínio à luz da concepção.",
      "context_indices": [
        0,
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "Registrar a identidade do responsável.",
      "note": "Obrigação complementar à presença de responsável em cada publicação.",
      "context_indices": [
        4,
        8
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção declarado é US$ 0,00.",
      "note": "Limite informado no campo max_build_cost_usd.",
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


## Matriz de achados, componentes e fontes

Cada registro vincula o achado derivado e seu digest às fontes exatas. Julgar significado e aplicabilidade, não só a existência da citação.

### criterion-1 — rule

```json
{
  "finding": {
    "id": "criterion-1",
    "kind": "rule",
    "text": "Cada publicação da equipe deve conter responsável e origem.",
    "condition": "Para cada publicação da equipe.",
    "outcome": "A publicação deve conter responsável e origem.",
    "exceptions": [],
    "impact": null,
    "rationale": "A identidade do responsável deve ser registrada, conforme a restrição de negócio.",
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
  "finding_sha256": "4ea1d7249e7a2be4d6c9cd80a76e52b626e7354463928148c3bc1b132547bd82",
  "literal_sources": [
    {
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Cada publicação da equipe deve conter responsável e origem.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "4ea1d7249e7a2be4d6c9cd80a76e52b626e7354463928148c3bc1b132547bd82",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Atom-8 exige expressamente responsável e origem em cada publicação da equipe."
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
      "note": "A expressão 'Cada publicação da equipe' estabelece o âmbito da condição."
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
    "rationale": "Finalidade declarada na concepção e na descrição do backlog.",
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
  "finding_sha256": "271e1b80eac6a986d15032888e12c44fb3eb2698ef104afd05c31fd7b7249d75",
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
      "finding_sha256": "271e1b80eac6a986d15032888e12c44fb3eb2698ef104afd05c31fd7b7249d75",
      "source_atom_ids": [
        "atom-1",
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Atom-1 declara a organização de publicações e fontes; atom-7 acrescenta o registro de decisões."
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
      "note": "O público declarado em atom-2 é autores."
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
    "rationale": "Princípios declarados; não especificam etapas adicionais de aprovação.",
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
  "finding_sha256": "2a67a7c3cf82c4b9859d0531ce27334194e5ed91f0a36db6deb4a9179448d057",
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
      "finding_sha256": "2a67a7c3cf82c4b9859d0531ce27334194e5ed91f0a36db6deb4a9179448d057",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram rastreabilidade e controle humano, sem definir etapas de aprovação."
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
    "text": "Gestão de workspace aplicada à organização de publicações e fontes.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Interpretação da declaração de domínio à luz da concepção.",
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
  "finding_sha256": "61370b2b73be87e707b72b236fb08e95db913d030e430e780b14cf88639e2082",
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
      "finding_sha256": "61370b2b73be87e707b72b236fb08e95db913d030e430e780b14cf88639e2082",
      "source_atom_ids": [
        "atom-1",
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Atom-9 declara workspace-management; atom-1 fornece a aplicação à organização de publicações e fontes."
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
    "text": "Registrar a identidade do responsável.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação complementar à presença de responsável em cada publicação.",
    "source_atom_ids": [
      "atom-5",
      "atom-8"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "4084935072d4172f67d744be65bb2acfd3e579950f583a98f32e2c62d0534f24",
  "literal_sources": [
    {
      "id": "atom-5",
      "source_ref": "input-3",
      "pointer": "/constraints/business/0",
      "quote": "Registrar a identidade do responsável.",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-8",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Cada publicação da equipe deve conter responsável e origem.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-5",
      "finding_sha256": "4084935072d4172f67d744be65bb2acfd3e579950f583a98f32e2c62d0534f24",
      "source_atom_ids": [
        "atom-5",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Atom-5 exige registrar a identidade do responsável; atom-8 exige responsável em cada publicação. A obrigação de identidade permanece separada."
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
    "text": "O custo máximo de construção declarado é US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite informado no campo max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "3a9258b46d53ffaf05ac70dba3fd5debb4d2f51defcbd3bcc546cf13c6b06d13",
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
      "finding_sha256": "3a9258b46d53ffaf05ac70dba3fd5debb4d2f51defcbd3bcc546cf13c6b06d13",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd de atom-6 informa 0.0."
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
      "note": "Controle humano representado sem inferir autorização."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Obrigação de registrar identidade representada separadamente."
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
      "note": "Organização de publicação e registro de decisões representados."
    },
    {
      "atom_id": "atom-9",
      "quote_sha256": "d8ec0dfaccceaea0a5f8ccf5a95f094560df5ea36683833d84877c601223e217",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Domínio declarado representado."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "a79c1f7e236f6dadc2d66f9ab1ce333e7c271bfe617435c1f8e49ce579b92ef2",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1",
        "context-5"
      ],
      "omission_ids": [],
      "note": "Regra de responsável e origem representada; vínculo com a obrigação de identidade preservado."
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
