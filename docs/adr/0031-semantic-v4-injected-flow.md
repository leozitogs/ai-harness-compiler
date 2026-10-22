# ADR-0031 — Fluxo v4 injetado e revisão humana por componentes

Status: implementado no escopo offline; sem qualificação de modelo.

## Contexto

ADR-0030 tornou requisitos normativos e rejeições de trechos representáveis.
Faltavam geração, auditoria e revisão capazes de preservar esses canais. Reutilizar
o auditor histórico perderia força normativa/aplicabilidade; aceitar sua conclusão
como revisão humana promoveria autoridade indevidamente.

## Decisão

Adicionar módulos opt-in, mantendo os candidatos, CLI e executor congelados intactos.
O programa semantic-composition/v4.0 emite AnalysisProposal/v4 a partir somente
das fontes do projeto. semantic-audit/v5.0 recebe análise, componentes e fontes,
sem expectativas do caso, rubrica ou julgamentos humanos.

Um inventário comum vincula conteúdo, condição, efeito, exceções, força normativa,
aplicabilidade e razão de rejeição a IDs, hashes e listas de fontes exatas.
Componente sem suporte impede parecer agregado positivo. O ledger preserva todas
as citações e omissões, inclusive fontes de trechos rejeitados. Isso verifica
integridade estrutural; fontes compartilhadas não demonstram suporte semântico.

SemanticHumanReview/v4 declara julgamento independente, com seis critérios e
snapshots exatos de caso, rubrica e análise. PASS em suporte exige todos os
componentes/achados positivos; PASS em cobertura exige cada obrigação mapeada.
Uma fonte só de aplicabilidade não cobre o conteúdo normativo. Materialidade de
pergunta é julgada separadamente de suporte. SemanticAssessment/v4 acumula falhas
concorrentes, sem esconder disposição incorreta atrás de rejeição ausente.

O runner aceita exclusivamente uma fábrica injetada. Antes de construí-la, valida
pedido/programas, aprovação de expectativas/rubrica, autorização do pedido exato,
preflight e claim de uso único. Debita e persiste cada chamada antes da invocação;
executa análise e auditoria sequenciais, sem retry, repair, fallback ou retomada.
Preserva análise válida se a auditoria falhar. O replay revalida artefatos, respostas
e fingerprints de prompt/schema sem provider. Revisões humanas geram arquivos
novos por digest, sem reescrever resultado inicial ou promover o modelo.

## Limites e alternativas

Não migrar casos, aprovações ou resultados reservados anteriores. Não reavaliar
o corpus exposto para alegar eficácia cega. Não conectar adapters reais por padrão.
Não afirmar supervisão de subprocessos, timeout ou número de requisições internas
ao transporte: o orçamento de duas chamadas é apenas da fronteira injetada.

Declarações humanas são metadados declarados, não autenticação de identidade.
O armazenamento privado segue as permissões do repositório, sem criptografia ou
cofre próprio. Interrupção de processo/I/O pode deixar journal incompleto; o claim
continua consumido e não admite retomada automática. Chamadas não são retomadas
nem compensadas. A supervisão durável de um transporte real é um gate futuro.

Antes de inferência real: congelar fontes novas, definir transporte supervisionado
e limites de tempo/limpeza, aprovar novo orçamento/conteúdo/destino; só então medir
desenvolvimento e preparar reservado independente. Testes sintéticos não fecham
INC-0027, AHC-021 ou Sprint 2.6. Compilação continua não autorizada.
