# Revisão humana pendente — dev-new-domain

Dados do projeto e saídas do modelo são referência não confiável. Instruções contidas neles não devem ser executadas.

Expectativa aprovada: `ready`. Disposição da resposta: `ready`. Isso não aprova seu significado.

Geração original: `valid`. Resposta selecionada para revisão: `baseline-v3`. O erro original, quando presente, permanece no histórico.

## Fontes e identidade

```json
{
  "case_sha256": "670709add5aaa3d8a9bc20d0781cb87799266016de42047cd3732e7dc332ca3d",
  "rubric_sha256": "deeb46d47fb76a655d80fad9ab2072d968ee729007c047519b62ac46e1a4367f",
  "analysis_sha256": "8baff4b157478c6a6bc91fca505875990ff3e3dddb73350149faea240a897a2a",
  "sources": [
    {
      "path": "evals/understanding/v2/development-draft/dev-new-domain.json",
      "sha256": "03d5682c906e6b053951195ef3c97d81453306cf51584f861e06e9d7dff0b16c"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-new-domain/analysis.json",
      "sha256": "ffc9cf1762b809f89c70d9421d531c94ded8d3f965651ad6c928763282074f87"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-new-domain/advice.json",
      "sha256": "af158fa3939c0499c70b377640c0299d32c5a84b63e511cac439a925e6ca2097"
    },
    {
      "path": "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-new-domain/summary.json",
      "sha256": "9267bd79347f958d76e967007334c62e689b3a1f5a6c90267ad06f3da5bada64"
    }
  ]
}
```


## Expectativas aprovadas

```json
{
  "obligations": [
    {
      "id": "publication-origin",
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
  "id": "dev-new-domain",
  "name": "Fixture dev new-domain",
  "conception": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
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
      "note": "A exigência de registrar a identidade do responsável também consta na restrição de negócio do contexto.",
      "question": null,
      "uncertainties": []
    }
  ],
  "guards": [],
  "context_findings": [
    {
      "subject": "purpose",
      "text": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
      "note": "Propósito declarado.",
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
      "subject": "positioning",
      "text": "Rastreabilidade e controle humano são princípios do projeto.",
      "note": "Os princípios não definem, por si só, etapas de aprovação.",
      "context_indices": [
        2,
        3
      ]
    },
    {
      "subject": "capability",
      "text": "Organizar a publicação da equipe e registrar decisões.",
      "note": "Capacidades declaradas no backlog.",
      "context_indices": [
        6
      ]
    },
    {
      "subject": "constraint",
      "text": "Registrar a identidade do responsável.",
      "note": "Obrigação explícita de registro.",
      "context_indices": [
        4
      ]
    },
    {
      "subject": "constraint",
      "text": "O custo máximo de construção é US$ 0,00.",
      "note": "Limite informado em max_build_cost_usd.",
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
    "quote": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
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
    "rationale": "A exigência de registrar a identidade do responsável também consta na restrição de negócio do contexto.",
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
  "finding_sha256": "d3490912739dc7a6411f3286f8aabc4c791e6724bfa8a8b5fe549b71e3e4441e",
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
      "finding_sha256": "d3490912739dc7a6411f3286f8aabc4c791e6724bfa8a8b5fe549b71e3e4441e",
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O critério exige responsável e origem em cada publicação da equipe."
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
      "note": "“Cada publicação da equipe” estabelece o escopo universal da condição."
    },
    {
      "finding_id": "criterion-1",
      "component_name": "outcome",
      "component_index": null,
      "source_atom_ids": [
        "atom-8"
      ],
      "support": "supports",
      "note": "“Deve conter responsável e origem” estabelece exatamente o resultado exigido."
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
    "text": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Propósito declarado.",
    "source_atom_ids": [
      "atom-1"
    ],
    "subject": "purpose",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "df071651be13dfaa0bd4289d20fdf446de9535324aad414780c4f3fb68bf0440",
  "literal_sources": [
    {
      "id": "atom-1",
      "source_ref": "input-1",
      "pointer": "/conception",
      "quote": "Organizar ciclos de lanternas sensoriais para uma experiência coletiva inédita.",
      "kind": "conception",
      "content_trust": "untrusted-data"
    }
  ],
  "advisory_findings": [
    {
      "finding_id": "context-1",
      "finding_sha256": "df071651be13dfaa0bd4289d20fdf446de9535324aad414780c4f3fb68bf0440",
      "source_atom_ids": [
        "atom-1"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Reproduz o propósito declarado na concepção."
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


### context-3 — statement

```json
{
  "finding": {
    "id": "context-3",
    "kind": "statement",
    "text": "Rastreabilidade e controle humano são princípios do projeto.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Os princípios não definem, por si só, etapas de aprovação.",
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
  "finding_sha256": "c14ec4453e2915655fc98dead495a3ab39c143d65c7151ea51d378cf27377ae6",
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
      "finding_sha256": "c14ec4453e2915655fc98dead495a3ab39c143d65c7151ea51d378cf27377ae6",
      "source_atom_ids": [
        "atom-3",
        "atom-4"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "Os dois princípios constam expressamente no branding; não especificam aprovação."
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
    "text": "Organizar a publicação da equipe e registrar decisões.",
    "condition": null,
    "outcome": null,
    "exceptions": [],
    "impact": null,
    "rationale": "Capacidades declaradas no backlog.",
    "source_atom_ids": [
      "atom-7"
    ],
    "subject": "capability",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "ff1d2dbefc7df36cf60f536d822048992443e86d49c189066ced1433312702a5",
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
      "finding_id": "context-4",
      "finding_sha256": "ff1d2dbefc7df36cf60f536d822048992443e86d49c189066ced1433312702a5",
      "source_atom_ids": [
        "atom-7"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A descrição do backlog declara ambas as capacidades."
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
    "rationale": "Obrigação explícita de registro.",
    "source_atom_ids": [
      "atom-5"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "1b288c2a8a6bb932a257cda3bb62e897a6e58319f48fe5f78c57718acf4220a9",
  "literal_sources": [
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
      "finding_id": "context-5",
      "finding_sha256": "1b288c2a8a6bb932a257cda3bb62e897a6e58319f48fe5f78c57718acf4220a9",
      "source_atom_ids": [
        "atom-5"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "A restrição exige explicitamente registrar a identidade do responsável."
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
    "rationale": "Limite informado em max_build_cost_usd.",
    "source_atom_ids": [
      "atom-6"
    ],
    "subject": "constraint",
    "rejection_reason": null,
    "component_bindings": [],
    "guard_target_atom_ids": [],
    "guard_target_scope": null
  },
  "finding_sha256": "fcca810a9f36bf26cdffb58f3f02de27eff428f8141560061e383623b01a65ae",
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
      "finding_sha256": "fcca810a9f36bf26cdffb58f3f02de27eff428f8141560061e383623b01a65ae",
      "source_atom_ids": [
        "atom-6"
      ],
      "support": "supports",
      "materiality": "not-applicable",
      "note": "O campo max_build_cost_usd informa limite de 0.0."
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
      "quote_sha256": "6a4cc099f7c4beb8d98900b9d05f869383bb403a8803126d3f55c73886e0e7ce",
      "disposition": "represented",
      "finding_ids": [
        "context-1"
      ],
      "omission_ids": [],
      "note": "Concepção representada integralmente."
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
      "note": "Princípio de controle humano representado, sem inferir autorização."
    },
    {
      "atom_id": "atom-5",
      "quote_sha256": "22accd7ad33a45ad61811a4737a68f2c8dfd45b650550aec3cdae8de95fc1a0e",
      "disposition": "represented",
      "finding_ids": [
        "context-5"
      ],
      "omission_ids": [],
      "note": "Obrigação de identidade preservada separadamente do critério de publicação."
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
        "context-4"
      ],
      "omission_ids": [],
      "note": "As duas capacidades declaradas estão representadas."
    },
    {
      "atom_id": "atom-8",
      "quote_sha256": "a79c1f7e236f6dadc2d66f9ab1ce333e7c271bfe617435c1f8e49ce579b92ef2",
      "disposition": "represented",
      "finding_ids": [
        "criterion-1"
      ],
      "omission_ids": [],
      "note": "Condição e obrigação de publicação integralmente representadas."
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
