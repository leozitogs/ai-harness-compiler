# Revisão humana pendente — dev-compatible-rules

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `ready`. Disposição da resposta: `ready`. Isso não aprova seu significado.

Geração original: `error`. Resposta selecionada para revisão: `schema-v31-recovery`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "f338181b253045093d1101f966cf863f3c7c51d94831becb88e0be60c8ad91ba",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "09f6148f4cf0303325d2c3380e32f2735a13f543797df23da3b0ca9b4e956581",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-compatible-rules.json",
      "sha256": "fc8a20bcd49950df782e5fc0e7ef39aea912e0b656b0198e24bfd546d7e96622"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/schema-v31-recovery/dev-compatible-rules/analysis.json",
      "sha256": "d2701f9b11e6b9c06d5c0603fc77bc6f452743892fa90b2cbb80e1110cbf6ea2"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/schema-v31-recovery/dev-compatible-rules/advice.json",
      "sha256": "7ec1bb51c60432cc95f3b30215d906cae768f7f1ecab1bd35bedc90ce2723534"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-compatible-rules/summary.json",
      "sha256": "3737a3464ba48cc7c2710a45d6a240f6a2a6c08c3f9efb5924c5d64281a44158"
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
      "quote": "Cada material tem título, autor e referência de origem.",
      "disposition": "rule"
    },
    {
      "id": "required-2",
      "source_pointer": "/backlog/0/acceptance_criteria/1",
      "quote": "Materiais só são visíveis ao educador responsável.",
      "disposition": "rule"
    },
    {
      "id": "required-3",
      "source_pointer": "/backlog/1/acceptance_criteria/0",
      "quote": "As afirmações do rascunho referenciam os materiais utilizados.",
      "disposition": "rule"
    },
    {
      "id": "required-4",
      "source_pointer": "/backlog/1/acceptance_criteria/1",
      "quote": "A publicação exige revisão e aprovação do educador.",
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
  "id": "learning-studio",
  "name": "Learning Studio",
  "conception": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
  "domain": "education",
  "branding": {
    "audience": [
      "educadores",
      "coordenadores pedagógicos"
    ],
    "tone": [
      "claro",
      "acolhedor",
      "preciso"
    ],
    "principles": [
      "fontes verificáveis",
      "controle do educador"
    ],
    "visual_constraints": [
      "interface acessível"
    ]
  },
  "backlog": [
    {
      "id": "material-library",
      "title": "Biblioteca de materiais",
      "description": "Permitir que o educador catalogue materiais e suas fontes.",
      "acceptance_criteria": [
        "Cada material tem título, autor e referência de origem.",
        "Materiais só são visíveis ao educador responsável."
      ],
      "depends_on": [],
      "inputs": [
        "material",
        "metadados de origem"
      ],
      "outputs": [
        "material catalogado"
      ],
      "data_owner": "educador",
      "side_effects": [
        "gravação na biblioteca"
      ],
      "risk": "medium",
      "implementation": "deterministic"
    },
    {
      "id": "lesson-draft",
      "title": "Rascunho de aula baseado em fontes",
      "description": "Preparar um rascunho de aula usando os materiais selecionados.",
      "acceptance_criteria": [
        "As afirmações do rascunho referenciam os materiais utilizados.",
        "A publicação exige revisão e aprovação do educador."
      ],
      "depends_on": [
        "material-library"
      ],
      "inputs": [
        "materiais selecionados",
        "objetivos de aprendizagem"
      ],
      "outputs": [
        "rascunho com referências"
      ],
      "data_owner": "educador",
      "side_effects": [],
      "risk": "medium",
      "implementation": "rag"
    }
  ],
  "constraints": {
    "technical": [
      "Python 3.12 ou superior",
      "contratos versionados"
    ],
    "security": [
      "não expor dados pessoais em traces"
    ],
    "business": [
      "revisão humana antes de publicação"
    ],
    "max_build_cost_usd": 0.0
  },
  "assets": [
    {
      "path": "assets/brand-notes.md",
      "description": "Referência visual e verbal; conteúdo não ingerido no MVP."
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
      "source_atom_id": "atom-16",
      "kind": "business-rule",
      "condition": {
        "text": "Para cada material catalogado.",
        "source_atom_ids": [
          "atom-16"
        ]
      },
      "outcome": {
        "text": "O material deve ter título, autor e referência de origem.",
        "source_atom_ids": [
          "atom-16"
        ]
      },
      "exceptions": [],
      "note": "Obrigação aplicável a cada material.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-17",
      "kind": "business-rule",
      "condition": {
        "text": "Quando um material for disponibilizado para visualização.",
        "source_atom_ids": [
          "atom-17"
        ]
      },
      "outcome": {
        "text": "A visibilidade deve ser restrita ao educador responsável.",
        "source_atom_ids": [
          "atom-17"
        ]
      },
      "exceptions": [],
      "note": "Não há exceção declarada para coordenadores pedagógicos.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-19",
      "kind": "business-rule",
      "condition": {
        "text": "Quando houver afirmações no rascunho de aula.",
        "source_atom_ids": [
          "atom-19"
        ]
      },
      "outcome": {
        "text": "As afirmações devem referenciar os materiais utilizados.",
        "source_atom_ids": [
          "atom-19"
        ]
      },
      "exceptions": [],
      "note": "Preserva a rastreabilidade das afirmações às fontes utilizadas.",
      "question": null,
      "uncertainties": []
    },
    {
      "source_atom_id": "atom-20",
      "kind": "business-rule",
      "condition": {
        "text": "Quando uma aula for submetida à publicação.",
        "source_atom_ids": [
          "atom-20"
        ]
      },
      "outcome": {
        "text": "A publicação exige revisão e aprovação do educador.",
        "source_atom_ids": [
          "atom-20"
        ]
      },
      "exceptions": [],
      "note": "Revisão e aprovação são condições necessárias para publicar.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [
    {
      "id": "guard-human-review",
      "condition": {
        "text": "Antes da publicação de conteúdo na plataforma.",
        "source_atom_ids": [
          "atom-1",
          "atom-13"
        ]
      },
      "effect": {
        "text": "Exigir revisão humana prévia.",
        "source_atom_ids": [
          "atom-1",
          "atom-13"
        ]
      },
      "target_scope": "project",
      "target_criterion_atom_ids": [],
      "note": "Restrição geral de publicação; não concede autorização para publicar."
    },
    {
      "id": "guard-trace-privacy",
      "condition": {
        "text": "Ao registrar traces.",
        "source_atom_ids": [
          "atom-12"
        ]
      },
      "effect": {
        "text": "Não expor dados pessoais.",
        "source_atom_ids": [
          "atom-12"
        ]
      },
      "target_scope": "project",
      "target_criterion_atom_ids": [],
      "note": "Restrição de segurança aplicável aos traces da plataforma."
    }
  ],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar materiais e preparar aulas baseadas em fontes, com revisão humana antes da publicação.",
      "note": "Propósito declarado da plataforma.",
      "context_indices": [
        0
      ]
    },
    {
      "subject": "audience",
      "text": "Educadores e coordenadores pedagógicos.",
      "note": "A identificação do público não concede permissões de acesso.",
      "context_indices": [
        1,
        2
      ]
    },
    {
      "subject": "tone",
      "text": "Comunicação clara, acolhedora e precisa.",
      "note": "Tom declarado.",
      "context_indices": [
        3,
        4,
        5
      ]
    },
    {
      "subject": "positioning",
      "text": "Fontes verificáveis e controle do educador.",
      "note": "Princípios declarados.",
      "context_indices": [
        6,
        7
      ]
    },
    {
      "subject": "constraint",
      "text": "Interface acessível.",
      "note": "Restrição de interface declarada.",
      "context_indices": [
        8
      ]
    },
    {
      "subject": "constraint",
      "text": "Python 3.12 ou superior e contratos versionados.",
      "note": "Restrições técnicas declaradas.",
      "context_indices": [
        9,
        10
      ]
    },
    {
      "subject": "constraint",
      "text": "Custo máximo de construção de US$ 0,00.",
      "note": "Limite declarado em max_build_cost_usd.",
      "context_indices": [
        13
      ]
    },
    {
      "subject": "capability",
      "text": "Catalogar materiais e suas fontes e preparar rascunhos de aula usando materiais selecionados.",
      "note": "Capacidades descritas no backlog.",
      "context_indices": [
        14,
        15
      ]
    },
    {
      "subject": "domain",
      "text": "Educação.",
      "note": "Domínio explicitamente declarado.",
      "context_indices": [
        16
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
    "quote": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
    "kind": "conception",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-2",
    "source_ref": "input-2",
    "pointer": "/branding/audience/0",
    "quote": "educadores",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-3",
    "source_ref": "input-2",
    "pointer": "/branding/audience/1",
    "quote": "coordenadores pedagógicos",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-4",
    "source_ref": "input-2",
    "pointer": "/branding/tone/0",
    "quote": "claro",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-5",
    "source_ref": "input-2",
    "pointer": "/branding/tone/1",
    "quote": "acolhedor",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-6",
    "source_ref": "input-2",
    "pointer": "/branding/tone/2",
    "quote": "preciso",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-7",
    "source_ref": "input-2",
    "pointer": "/branding/principles/0",
    "quote": "fontes verificáveis",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-8",
    "source_ref": "input-2",
    "pointer": "/branding/principles/1",
    "quote": "controle do educador",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-9",
    "source_ref": "input-2",
    "pointer": "/branding/visual_constraints/0",
    "quote": "interface acessível",
    "kind": "branding",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-10",
    "source_ref": "input-3",
    "pointer": "/constraints/technical/0",
    "quote": "Python 3.12 ou superior",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-11",
    "source_ref": "input-3",
    "pointer": "/constraints/technical/1",
    "quote": "contratos versionados",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-12",
    "source_ref": "input-3",
    "pointer": "/constraints/security/0",
    "quote": "não expor dados pessoais em traces",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-13",
    "source_ref": "input-3",
    "pointer": "/constraints/business/0",
    "quote": "revisão humana antes de publicação",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-14",
    "source_ref": "input-3",
    "pointer": "/constraints/max_build_cost_usd",
    "quote": "0.0",
    "kind": "constraint",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-15",
    "source_ref": "input-4",
    "pointer": "/backlog/0/description",
    "quote": "Permitir que o educador catalogue materiais e suas fontes.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-16",
    "source_ref": "input-5",
    "pointer": "/backlog/0/acceptance_criteria/0",
    "quote": "Cada material tem título, autor e referência de origem.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-17",
    "source_ref": "input-6",
    "pointer": "/backlog/0/acceptance_criteria/1",
    "quote": "Materiais só são visíveis ao educador responsável.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-18",
    "source_ref": "input-7",
    "pointer": "/backlog/1/description",
    "quote": "Preparar um rascunho de aula usando os materiais selecionados.",
    "kind": "backlog-description",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-19",
    "source_ref": "input-8",
    "pointer": "/backlog/1/acceptance_criteria/0",
    "quote": "As afirmações do rascunho referenciam os materiais utilizados.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-20",
    "source_ref": "input-9",
    "pointer": "/backlog/1/acceptance_criteria/1",
    "quote": "A publicação exige revisão e aprovação do educador.",
    "kind": "acceptance-criterion",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-21",
    "source_ref": "input-10",
    "pointer": "/domain",
    "quote": "education",
    "kind": "domain-declaration",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-22",
    "source_ref": "input-11",
    "pointer": "/assets/0/path",
    "quote": "assets/brand-notes.md",
    "kind": "asset-metadata",
    "content_trust": "untrusted-data"
  },
  {
    "id": "atom-23",
    "source_ref": "input-11",
    "pointer": "/assets/0/description",
    "quote": "Referência visual e verbal; conteúdo não ingerido no MVP.",
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
    "text": "Cada material tem título, autor e referência de origem.",
    "condition": "Para cada material catalogado.",
    "outcome": "O material deve ter título, autor e referência de origem.",
    "exceptions": [],
    "impact": null,
    "rationale": "Obrigação aplicável a cada material.",
    "source_atom_ids": [
      "atom-16"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-16"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-16"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "df91a95e5c94578f8d13ce5e9e2bacd423159038ac0419ea82bb133a71ce5aa3",
  "literal_sources": [
    {
      "id": "atom-16",
      "source_ref": "input-5",
      "pointer": "/backlog/0/acceptance_criteria/0",
      "quote": "Cada material tem título, autor e referência de origem.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-1",
      "finding_sha256": "df91a95e5c94578f8d13ce5e9e2bacd423159038ac0419ea82bb133a71ce5aa3",
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige título, autor e referência de origem para cada material."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-1",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "note": "Cada material estabelece aplicação individual no contexto de catalogação."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-16"
      ],
      "support": "supports",
      "note": "Os três campos exigidos constam expressamente."
    }
  ],
  "human_support": "not-run"
}
```


### criterion-2 — rule

```json
{
  "finding": {
    "id": "criterion-2",
    "kind": "rule",
    "text": "Materiais só são visíveis ao educador responsável.",
    "condition": "Quando um material for disponibilizado para visualização.",
    "outcome": "A visibilidade deve ser restrita ao educador responsável.",
    "exceptions": [],
    "impact": null,
    "rationale": "Não há exceção declarada para coordenadores pedagógicos.",
    "source_atom_ids": [
      "atom-17"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-17"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-17"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "7f2320d14d56d6004c584f3b68e2bac8bd2194e9d059f8f1bf631e13e70901ef",
  "literal_sources": [
    {
      "id": "atom-17",
      "source_ref": "input-6",
      "pointer": "/backlog/0/acceptance_criteria/1",
      "quote": "Materiais só são visíveis ao educador responsável.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-2",
      "finding_sha256": "7f2320d14d56d6004c584f3b68e2bac8bd2194e9d059f8f1bf631e13e70901ef",
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte restringe expressamente a visibilidade ao educador responsável, sem exceções."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-2",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "note": "A restrição se aplica à visualização dos materiais."
    },
    {
      "finding_id": "criterion-2",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-17"
      ],
      "support": "supports",
      "note": "Só o educador responsável pode visualizar."
    }
  ],
  "human_support": "not-run"
}
```


### criterion-3 — rule

```json
{
  "finding": {
    "id": "criterion-3",
    "kind": "rule",
    "text": "As afirmações do rascunho referenciam os materiais utilizados.",
    "condition": "Quando houver afirmações no rascunho de aula.",
    "outcome": "As afirmações devem referenciar os materiais utilizados.",
    "exceptions": [],
    "impact": null,
    "rationale": "Preserva a rastreabilidade das afirmações às fontes utilizadas.",
    "source_atom_ids": [
      "atom-19"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-19"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-19"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "b0ed268f97ffd94f6ed8fcb43bbba2ecb5e95dd13d76bb01821b1d5530f8f277",
  "literal_sources": [
    {
      "id": "atom-19",
      "source_ref": "input-8",
      "pointer": "/backlog/1/acceptance_criteria/0",
      "quote": "As afirmações do rascunho referenciam os materiais utilizados.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-3",
      "finding_sha256": "b0ed268f97ffd94f6ed8fcb43bbba2ecb5e95dd13d76bb01821b1d5530f8f277",
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte exige referências aos materiais utilizados nas afirmações do rascunho."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-3",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "note": "A fonte trata das afirmações presentes no rascunho."
    },
    {
      "finding_id": "criterion-3",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-19"
      ],
      "support": "supports",
      "note": "As afirmações devem referenciar os materiais utilizados."
    }
  ],
  "human_support": "not-run"
}
```


### criterion-4 — rule

```json
{
  "finding": {
    "id": "criterion-4",
    "kind": "rule",
    "text": "A publicação exige revisão e aprovação do educador.",
    "condition": "Quando uma aula for submetida à publicação.",
    "outcome": "A publicação exige revisão e aprovação do educador.",
    "exceptions": [],
    "impact": null,
    "rationale": "Revisão e aprovação são condições necessárias para publicar.",
    "source_atom_ids": [
      "atom-20"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-20"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-20"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "409a1dcd028c682edd56eaf1dea9585bf3cc194e1d1ad4a9a8a5ff156aee2018",
  "literal_sources": [
    {
      "id": "atom-20",
      "source_ref": "input-9",
      "pointer": "/backlog/1/acceptance_criteria/1",
      "quote": "A publicação exige revisão e aprovação do educador.",
      "kind": "acceptance-criterion",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "criterion-4",
      "finding_sha256": "409a1dcd028c682edd56eaf1dea9585bf3cc194e1d1ad4a9a8a5ff156aee2018",
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Revisão e aprovação do educador são requisitos explícitos de publicação."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "criterion-4",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "note": "A publicação é o evento sujeito ao requisito."
    },
    {
      "finding_id": "criterion-4",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-20"
      ],
      "support": "supports",
      "note": "A fonte exige tanto revisão quanto aprovação do educador."
    }
  ],
  "human_support": "not-run"
}
```


### guard-human-review — rule

```json
{
  "finding": {
    "id": "guard-human-review",
    "kind": "rule",
    "text": "Exigir revisão humana prévia.",
    "condition": "Antes da publicação de conteúdo na plataforma.",
    "outcome": "Exigir revisão humana prévia.",
    "exceptions": [],
    "impact": null,
    "rationale": "Restrição geral de publicação; não concede autorização para publicar.",
    "source_atom_ids": [
      "atom-1",
      "atom-13"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-1",
          "atom-13"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-1",
          "atom-13"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": "project"
  },
  "finding_sha256": "3a4d8443bf5441acb303c924c14be9f59d44e5cc2e8833bd325b2ae0dfefefb6",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
      "kind": "conception",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-13",
      "source_ref": "input-3",
      "pointer": "/constraints/business/0",
      "quote": "revisão humana antes de publicação",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "guard-human-review",
      "finding_sha256": "3a4d8443bf5441acb303c924c14be9f59d44e5cc2e8833bd325b2ae0dfefefb6",
      "source_atom_ids": [
        "atom-1",
        "atom-13"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Ambas as fontes exigem revisão humana anterior à publicação; isso não concede autorização."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "guard-human-review",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-1",
        "atom-13"
      ],
      "support": "supports",
      "note": "Ambas situam o requisito antes da publicação."
    },
    {
      "finding_id": "guard-human-review",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-1",
        "atom-13"
      ],
      "support": "supports",
      "note": "Ambas exigem revisão humana prévia."
    }
  ],
  "human_support": "not-run"
}
```


### guard-trace-privacy — rule

```json
{
  "finding": {
    "id": "guard-trace-privacy",
    "kind": "rule",
    "text": "Não expor dados pessoais.",
    "condition": "Ao registrar traces.",
    "outcome": "Não expor dados pessoais.",
    "exceptions": [],
    "impact": null,
    "rationale": "Restrição de segurança aplicável aos traces da plataforma.",
    "source_atom_ids": [
      "atom-12"
    ],
    "subject": null,
    "rejection_reason": null,
    "component_bindings": [
      {
        "name": "condition",
        "index": null,
        "source_atom_ids": [
          "atom-12"
        ]
      },
      {
        "name": "outcome",
        "index": null,
        "source_atom_ids": [
          "atom-12"
        ]
      }
    ],
    "guard_target_atom_ids": [],
    "guard_target_scope": "project"
  },
  "finding_sha256": "2b4c8a46ab397424a23e850b736e971f4457c7b1b117ad7755dc2277b374d0b3",
  "literal_sources": [
    {
      "id": "atom-12",
      "source_ref": "input-3",
      "pointer": "/constraints/security/0",
      "quote": "não expor dados pessoais em traces",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "guard-trace-privacy",
      "finding_sha256": "2b4c8a46ab397424a23e850b736e971f4457c7b1b117ad7755dc2277b374d0b3",
      "source_atom_ids": [
        "atom-12"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A fonte proíbe exposição de dados pessoais em traces."
    }
  ],
  "advisory_components": [
    {
      "finding_id": "guard-trace-privacy",
      "component_name": "condition",
      "component_index": null,
      "source_atom_ids": [
        "atom-12"
      ],
      "support": "supports",
      "note": "A proibição tem traces como contexto explícito."
    },
    {
      "finding_id": "guard-trace-privacy",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-12"
      ],
      "support": "supports",
      "note": "A fonte proíbe expor dados pessoais nesse contexto."
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
    "text": "Organizar materiais e preparar aulas baseadas em fontes, com revisão humana antes da publicação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Propósito declarado da plataforma.",
    "source_atom_ids": [
      "atom-1"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "60b73f42a8932e35705a94fe16c91f66ad4ab5d149548f07f90ee5f9c5bc2c5c",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Uma plataforma para educadores organizarem materiais e prepararem aulas baseadas em fontes, com revisão humana antes da publicação.",
      "kind": "conception",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-1",
      "finding_sha256": "60b73f42a8932e35705a94fe16c91f66ad4ab5d149548f07f90ee5f9c5bc2c5c",
      "source_atom_ids": [
        "atom-1"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O propósito e a revisão humana prévia constam da concepção."
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
    "text": "Educadores e coordenadores pedagógicos.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "A identificação do público não concede permissões de acesso.",
    "source_atom_ids": [
      "atom-2",
      "atom-3"
    ],
    "subject": "audience",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "e03e208a0409313f45df949bfc19e73c41468750b6d551c01fbd3c93f4611984",
  "literal_sources": [
    {
      "id": "atom-2",
      "source_ref": "input-2",
      "pointer": "/branding/audience/0",
      "quote": "educadores",
      "kind": "branding",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-3",
      "source_ref": "input-2",
      "pointer": "/branding/audience/1",
      "quote": "coordenadores pedagógicos",
      "kind": "branding",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-2",
      "finding_sha256": "e03e208a0409313f45df949bfc19e73c41468750b6d551c01fbd3c93f4611984",
      "source_atom_ids": [
        "atom-2",
        "atom-3"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes identificam os dois públicos, sem conceder acesso."
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
    "text": "Comunicação clara, acolhedora e precisa.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Tom declarado.",
    "source_atom_ids": [
      "atom-4",
      "atom-5",
      "atom-6"
    ],
    "subject": "tone",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "dc4cc56e3a25b94678ff6925258221635d383516cc4035dcd602d76a503598ee",
  "literal_sources": [
    {
      "id": "atom-4",
      "source_ref": "input-2",
      "pointer": "/branding/tone/0",
      "quote": "claro",
      "kind": "branding",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-5",
      "source_ref": "input-2",
      "pointer": "/branding/tone/1",
      "quote": "acolhedor",
      "kind": "branding",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-6",
      "source_ref": "input-2",
      "pointer": "/branding/tone/2",
      "quote": "preciso",
      "kind": "branding",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-3",
      "finding_sha256": "dc4cc56e3a25b94678ff6925258221635d383516cc4035dcd602d76a503598ee",
      "source_atom_ids": [
        "atom-4",
        "atom-5",
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os três atributos de tom estão explícitos."
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
    "text": "Fontes verificáveis e controle do educador.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Princípios declarados.",
    "source_atom_ids": [
      "atom-7",
      "atom-8"
    ],
    "subject": "positioning",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "3a5b38afcee60aeeded2ae3bcfb20f515886dabc6b7e15e207755564f5e3dab7",
  "literal_sources": [
    {
      "id": "atom-7",
      "source_ref": "input-2",
      "pointer": "/branding/principles/0",
      "quote": "fontes verificáveis",
      "kind": "branding",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-8",
      "source_ref": "input-2",
      "pointer": "/branding/principles/1",
      "quote": "controle do educador",
      "kind": "branding",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-4",
      "finding_sha256": "3a5b38afcee60aeeded2ae3bcfb20f515886dabc6b7e15e207755564f5e3dab7",
      "source_atom_ids": [
        "atom-7",
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes declaram verificabilidade e controle do educador."
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
    "text": "Interface acessível.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Restrição de interface declarada.",
    "source_atom_ids": [
      "atom-9"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "dd59bf0b810573b17042ec1105ac4fbdd58d5d3a836e1e82bb7d007c60d0e1e1",
  "literal_sources": [
    {
      "id": "atom-9",
      "source_ref": "input-2",
      "pointer": "/branding/visual_constraints/0",
      "quote": "interface acessível",
      "kind": "branding",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-5",
      "finding_sha256": "dd59bf0b810573b17042ec1105ac4fbdd58d5d3a836e1e82bb7d007c60d0e1e1",
      "source_atom_ids": [
        "atom-9"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Acessibilidade da interface é uma restrição explícita."
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
    "text": "Python 3.12 ou superior e contratos versionados.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Restrições técnicas declaradas.",
    "source_atom_ids": [
      "atom-10",
      "atom-11"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "171ce65f6bac851d0806d78df72851dbad644a901b141b8f2754b9a5f4d45241",
  "literal_sources": [
    {
      "id": "atom-10",
      "source_ref": "input-3",
      "pointer": "/constraints/technical/0",
      "quote": "Python 3.12 ou superior",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-11",
      "source_ref": "input-3",
      "pointer": "/constraints/technical/1",
      "quote": "contratos versionados",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-6",
      "finding_sha256": "171ce65f6bac851d0806d78df72851dbad644a901b141b8f2754b9a5f4d45241",
      "source_atom_ids": [
        "atom-10",
        "atom-11"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes especificam a versão mínima de Python e contratos versionados."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-7 — statement

```json
{
  "finding": {
    "id": "context-7",
    "kind": "statement",
    "text": "Custo máximo de construção de US$ 0,00.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Limite declarado em max_build_cost_usd.",
    "source_atom_ids": [
      "atom-14"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "794cb5423b3d1d70d2d48e88c854d18e5b4a8e1f474a5f86329ad50590c88805",
  "literal_sources": [
    {
      "id": "atom-14",
      "source_ref": "input-3",
      "pointer": "/constraints/max_build_cost_usd",
      "quote": "0.0",
      "kind": "constraint",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-7",
      "finding_sha256": "794cb5423b3d1d70d2d48e88c854d18e5b4a8e1f474a5f86329ad50590c88805",
      "source_atom_ids": [
        "atom-14"
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


### context-8 — statement

```json
{
  "finding": {
    "id": "context-8",
    "kind": "statement",
    "text": "Catalogar materiais e suas fontes e preparar rascunhos de aula usando materiais selecionados.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades descritas no backlog.",
    "source_atom_ids": [
      "atom-15",
      "atom-18"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "ac8f5549da2c50c4d94cea7c9d6978a4720ab9eb8f516b3ff2d99515bb5c93af",
  "literal_sources": [
    {
      "id": "atom-15",
      "source_ref": "input-4",
      "pointer": "/backlog/0/description",
      "quote": "Permitir que o educador catalogue materiais e suas fontes.",
      "kind": "backlog-description",
      "content_trust": "untrusted-data"
    },
    {
      "id": "atom-18",
      "source_ref": "input-7",
      "pointer": "/backlog/1/description",
      "quote": "Preparar um rascunho de aula usando os materiais selecionados.",
      "kind": "backlog-description",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-8",
      "finding_sha256": "ac8f5549da2c50c4d94cea7c9d6978a4720ab9eb8f516b3ff2d99515bb5c93af",
      "source_atom_ids": [
        "atom-15",
        "atom-18"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "As fontes descrevem catalogação pelo educador e preparação com materiais selecionados."
    }
  ],
  "advisory_components": [],
  "human_support": "not-run"
}
```


### context-9 — domain

```json
{
  "finding": {
    "id": "context-9",
    "kind": "domain",
    "text": "Educação.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Domínio explicitamente declarado.",
    "source_atom_ids": [
      "atom-21"
    ],
    "subject": "domain",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "8046ed7a4e968c7b87962ce6e0c36529e3ce9685988e550e39913c792b4e8f78",
  "literal_sources": [
    {
      "id": "atom-21",
      "source_ref": "input-10",
      "pointer": "/domain",
      "quote": "education",
      "kind": "domain-declaration",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-9",
      "finding_sha256": "8046ed7a4e968c7b87962ce6e0c36529e3ce9685988e550e39913c792b4e8f78",
      "source_atom_ids": [
        "atom-21"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Educação corresponde ao domínio declarado como education."
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
      "text": "Como se determina o educador responsável por um material e qual educador pode revisar e aprovar a publicação da aula?",
      "rationale": "As fontes restringem acesso e exigem aprovação, mas não definem a atribuição dessas responsabilidades nem estabelecem se pertencem à mesma pessoa.",
      "source_atom_ids": [
        "atom-17",
        "atom-20"
      ],
      "impact": "authorization"
    }
  ],
  "source_coverage": [
    {
      "atom_id": "atom-1",
      "quote_sha256": "6b1e42851e6b8515c7190f3acc926e4cfb328a53aaf17678156fa2350c35fe95",
      "disposition": "represented",
      "finding_ids": [
        "guard-human-review",
        "context-1"
      ],
      "omission_ids": [],
      "note": "Concepção e revisão prévia representadas."
    },
    {
      "atom_id": "atom-2",
      "quote_sha256": "6f9e4050f26e11615351b7b695a5f5bedd8591d0b0557c05056ae6ca7f702f50",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público representado."
    },
    {
      "atom_id": "atom-3",
      "quote_sha256": "caf6c915a0adb43c362a413ec22f04d1f1405cfb3f9998f4c722cc811495a14a",
      "disposition": "represented",
      "finding_ids": [
        "context-2"
      ],
      "omission_ids": [],
      "note": "Público representado; não implica permissão de acesso."
    },
    {
      "atom_id": "atom-4",
      "quote_sha256": "bdae5d555cce9e9bb1828b74b1dfa90f1c3a65d5ed322e06c3e38609b7f4823f",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom claro representado."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "5fcd5ac268c8a79c4c06d537c621653be7bfdbaf396a3ea67272b17e903ebd80",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom acolhedor representado."
    },
    {
      "atom_id": "atom-6",
      "quote_sha256": "6398bad0d1c9c033b689e5356a3508389fc537bb10bdc26f0b49fa723dc90c7d",
      "disposition": "represented",
      "finding_ids": [
        "context-3"
      ],
      "omission_ids": [],
      "note": "Tom preciso representado."
    },
    {
      "atom_id": "atom-7",
      "quote_sha256": "cdcc2409dcbbd79f68e88e2e825e96687492d6f7ecff72ebaaf4eab385025f83",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Princípio de fontes verificáveis representado."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "54d11f2ad21a073d7e949afde270223730ec58eea046afb9767244b35cc586bc",
      "disposition": "represented",
      "finding_ids": [
        "context-4"
      ],
      "omission_ids": [],
      "note": "Controle do educador representado."
    },
    {
      "atom_id": "atom-9",
      "quote_sha256": "37dc387dfd2c4dcc23b99e59ae48a1baf860b032c9b7cee1bc2cd4b0d59b4742",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Restrição de acessibilidade representada."
    },
    {
      "atom_id": "atom-10",
      "quote_sha256": "3821baa85deb28950411e56953927f45af87e0a728d986031c058603caf5e1c8",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Restrição de Python representada."
    },
    {
      "atom_id": "atom-11",
      "quote_sha256": "6c8c51d22c903bcf20655c5144f6d989a99c35e6cf9e4951f4c8eb3b1927754d",
      "disposition": "represented",
      "finding_ids": [
        "context-6"
      ],
      "omission_ids": [],
      "note": "Versionamento de contratos representado."
    },
    {
      "atom_id": "atom-12",
      "quote_sha256": "6478d143ac8b69895c72097fb00c45295bad95897de88bb4592e63b8914e1637",
      "disposition": "represented",
      "finding_ids": [
        "guard-trace-privacy"
      ],
      "omission_ids": [],
      "note": "Restrição de privacidade representada separadamente."
    },
    {
      "atom_id": "atom-13",
      "quote_sha256": "d8b7fccf2b4a31be4c721e436190f938b2f1e03ca0c4d691864ed5a1b4561f33",
      "disposition": "represented",
      "finding_ids": [
        "guard-human-review"
      ],
      "omission_ids": [],
      "note": "Revisão humana prévia representada separadamente."
    },
    {
      "atom_id": "atom-14",
      "quote_sha256": "8aed642bf5118b9d3c859bd4be35ecac75b6e873cce34e7b6f554b06f75550d7",
      "disposition": "represented",
      "finding_ids": [
        "context-7"
      ],
      "omission_ids": [],
      "note": "Limite de custo representado."
    },
    {
      "atom_id": "atom-15",
      "quote_sha256": "3fb9a9c8225ab5a8fb76ef8e2b80f2bf8d752c02d5792345edc73b3124b42549",
      "disposition": "represented",
      "finding_ids": [
        "context-8"
      ],
      "omission_ids": [],
      "note": "Capacidade de catalogação representada."
    },
    {
      "atom_id": "atom-18",
      "quote_sha256": "f8a24f791bf5b85fbeaf21d5ce87a5aa89b2607a6dbf71a906872cc1d98d16dc",
      "disposition": "represented",
      "finding_ids": [
        "context-8"
      ],
      "omission_ids": [],
      "note": "Preparação com materiais selecionados representada."
    },
    {
      "atom_id": "atom-21",
      "quote_sha256": "68bf0109c6f8a87bfa96d1ecd9503326ba35cf4a6086988a1d2c8a20fbef00d1",
      "disposition": "represented",
      "finding_ids": [
        "context-9"
      ],
      "omission_ids": [],
      "note": "Domínio representado."
    },
    {
      "atom_id": "atom-16",
      "quote_sha256": "1c22b4c7b58ee92b7c21483afc80020fd4232e80f2c81b95ff7a3e4cfd8e6f0e",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Campos obrigatórios representados."
    },
    {
      "atom_id": "atom-17",
      "quote_sha256": "87b05e3851eb9a5e12ef9326599a17b615cbd7e06106fd39df19b6ae423cbd93",
      "disposition": "missing",
      "finding_ids": [
        "criterion-2"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Restrição representada; atribuição do educador responsável permanece indefinida."
    },
    {
      "atom_id": "atom-19",
      "quote_sha256": "ecf4bb47b217cf3dc704089e2056fd1cbffaed0ab081d1f0dec726a68d33b60e",
      "disposition": "represented",
      "finding_ids": [
        "criterion-3"
      ],
      "omission_ids": [],
      "note": "Referências das afirmações representadas."
    },
    {
      "atom_id": "atom-20",
      "quote_sha256": "6a4337aa2ca248e7621e409463d8ddb97aada7996a5684315e032b1548ae16f0",
      "disposition": "missing",
      "finding_ids": [
        "criterion-4"
      ],
      "omission_ids": [
        "omission-1"
      ],
      "note": "Requisitos representados; identidade do educador habilitado a aprovar permanece indefinida."
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
