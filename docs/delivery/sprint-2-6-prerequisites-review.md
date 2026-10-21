# Consolidação de revisão — AHC-021 e AHC-022

Esta matriz confronta o backlog canônico com evidências atuais. Não é aceite de
história nem autorização de avaliação reservada. Os 48 aceites humanos da rodada
v3.4 dizem respeito às oito análises identificadas por hash, não a todos os critérios
de entrega das histórias.

## AHC-021 — rubrica e evals

| Critério | Evidência | Limite ou trabalho restante |
| --- | --- | --- |
| Dataset versionado, desenvolvimento/reservado separados e expectativas congeladas | `evals/understanding/v2/development-approved-manifest.json`: oito inputs e rubrica congelados, expectativas aprovadas pelo PO | Parcial: o manifesto declara `holdout: not-read-not-migrated`. O freeze v1 declara expectativas propostas; não equivale a um reservado v2 revisado. Preparar protocolo de compatibilidade e revisão independente antes de avaliar. |
| Runner com estados, fingerprints, tentativas e evidências | Contratos de assessment, runner supervisionado, recibos/protocolo e testes; os snapshots iniciais `not-run` e o erro da auditoria foram preservados | Modelo solicitado conhecido; digest imutável e parâmetros efetivamente observados continuam desconhecidos. Não inventar metadados ou confundir hashes de programa/saída com digest do modelo. Perfis AHC-024 devem tratar isso explicitamente. |
| Revisão de cobertura, suporte, conflitos e assets; separação de autoridade | Manifesto humano v3.4: oito passes, 48 critérios aceitos, zero pendentes; resposta inválida do auditor mantida separada | Evidenciado no desenvolvimento. Não generaliza para dados novos, não autentica independentemente o revisor e não aprova runtime ou compilação. |

O reservado foi inspecionado somente por metadados do freeze v1 e declaração do
manifesto de desenvolvimento. Nenhum conteúdo de caso reservado foi lido para
esta correção ou usado para ajustar o schema.

## AHC-022 — grounding e cobertura

| Critério | Evidência | Limite ou trabalho restante |
| --- | --- | --- |
| Representações tipadas separam declarações, hipóteses, regras, dúvidas e conflitos | Análises v3.4 e revisões humanas completas preservam regras, papéis, fontes, obrigação normativa e assets não lidos | Evidenciado nesses snapshots; não é garantia universal ou enforcement executável. |
| Prompt/decomposição versionados, tuning só em desenvolvimento e gates de suporte/cobertura | Receitas v3.1–v3.4 explícitas; fingerprints históricos testados; reviews por snapshot e validação estrita | Nova receita de auditoria v4.1 é opt-in, testada offline e ainda não exercitada no provider; INC-0025 não foi apagado. Default continua histórico. |
| Comparação por rubrica congelada, regressões e tentativas limitadas | Matriz humana histórica 5 pass/3 fail; v3.3 6 pass/2 fail; v3.4 8 pass. Protocolos conservam todas as tentativas e budgets encerrados. Relatórios AHC-021 conservam as reproduções negativas de INC-0007 | Referências históricas incluem tentativas diferentes; não são experimento causal/repetido AHC-025. Os modelos locais de INC-0007 não foram corrigidos ou qualificados por aprovar análises de outro modelo. |

## Gate recomendado

O PR #60 foi integrado após checks verdes. A correção estrutural do auditor segue
em incremento separado; CI e replay offline validam código/contratos, não eficácia
de decodificação ou qualidade em dados novos.

Antes de encerrar os pré-requisitos, consolidar a revisão de entrega, definir a
compatibilidade da avaliação reservada com a rubrica/contratos atuais e registrar
as limitações de metadados. Não marcar as histórias como Done por esta matriz.
AHC-024 continua pelo gate de revisão das duas histórias, sem acrescentar uma
dependência artificial em AHC-023. Qualificação, comparação repetida, promoção e
fine-tuning permanecem em seus gates próprios.

Para preparar avaliação reservada: primeiro congelar candidato e receita completa;
separar projetos/famílias dos casos de desenvolvimento; ter expectativas revisadas
por responsável independente do candidato; registrar hashes, escopo, budget,
repetições e autorização antes de qualquer acesso/execução. Não migrar o reservado
v1 automaticamente nem fabricar dados reservados a partir de falhas de desenvolvimento.

Fontes principais: `project-definition/project.yaml`, `docs/delivery/scrum.md`,
`docs/delivery/sprint-2-6-kickoff.md`,
`docs/delivery/sprint-2-6-v34-development.md`,
`docs/evidence/sprint-2-6-v34-development-20261020/human-review/manifest.json` e
`knowledge/records/INC/INC-0007/`.

Atualização de 21/10/2026: o [smoke autorizado](sprint-2-6-bound-audit-smoke.md)
exercitou a receita de auditoria v4.1 no provider com uma resposta estruturalmente
válida. A pendência de compatibilidade desse snapshot foi verificada; não substitui
avaliação semântica, estabilidade, revisão de entrega ou o gate de reservado v2.
