# Contratos semânticos v4 e preflight offline

A migração adiciona representação explícita para requisitos de qualquer fonte
literal elegível. Não altera os prompts, defaults, casos, avaliações ou runner v3.
Motivação e limites: [ADR-0030](../adr/0030-versioned-semantic-representability.md).

## Plano de implementação e verificação

| Etapa | Depende de | Verificação |
| --- | --- | --- |
| Novos contratos de análise/caso | Diagnóstico INC-0027 e decisões específicas do PO | Requirement fora de critérios; fato não promovido automaticamente |
| Separar rejeições | Novos canais tipados | Rejeitar trecho mantém ready/blocked; projeto continua independente |
| Preflight | Caso validado e alvo explícito | Expectativa inexpressável detectada sem provider; relatório contraditório recusado |
| Fronteira de arquivos | Preflight puro | Limites de leitura, saída nova, mensagens sem fontes; nenhum SDK de modelo importado |
| Schemas e compatibilidade | Contratos estabilizados | Novos schemas exportados; bytes dos schemas e fontes históricos preservados |
| Qualidade e memória | Regressões sintéticas | Checks, build, registros imutáveis e PR; sem alegar qualidade do modelo |

## Semântica dos novos canais

RequirementV4 exige id, content (text/source_atom_ids), normative_force
(required/prohibited) e note; applicability é opcional e tem evidência própria.
O conteúdo e sua aplicabilidade não podem citar átomos desconhecidos ou metadados
de assets como se fossem conteúdo lido. IDs são únicos entre critérios, guards,
fatos, requisitos e rejeições. As regras/guards retêm condição/efeito/exceções e
fontes independentes; a nova representação não executa qualquer regra.

ContentRejectionV4 tem id, conteúdo ancorado, reason=untrusted-instruction e nota.
A disposição depende somente de project_analysis: ready, blocked ou safely-rejected.
Uma rejeição de trecho não limpa conflito/pergunta material legítimos, não cria
bloqueio e não autoriza compilação. O canal de projeto só mantém a razão histórica
unread-required-source para safe-rejection; a injeção deve usar content_rejections.

Texto factual em context_findings permanece statement/domain. Requisito novo é
uma declaração normativa explícita no canal requirements; não existe equivalência
automática entre texto factual, requisito e regra. Vincular fonte só estabelece
proveniência estrutural; força normativa e suporte exigem futura revisão semântica
vinculada aos componentes novos. O review v3 não aceita uma análise v4.

## Caso e preflight

AssessmentCase/v3 distingue required_content_rejection_pointers e
required_project_rejection_pointers. expected_behavior descreve o projeto inteiro.
Um caso ready pode exigir rejeitar um trecho, mantendo obrigações legítimas.
Cada obrigação ainda cita exatamente uma fonte literal. statement/domain também
são expectativas possíveis sem transformar a declaração em obrigação normativa.
A aprovação de expectativas continua separada de aprovação de saída/execução.

```sh
python scripts/preflight_semantic_case.py --case development-case-v3.json --target SemanticAnalysis/v4 --output .factory/new-preflight.json
```

O JSON precisa declarar AssessmentCase/v2 ou AssessmentCase/v3 explicitamente.
Target deve ser SemanticAnalysis/v3 ou SemanticAnalysis/v4; versão desconhecida não
usa fallback. Código 0 significa compatível; código 2 indica incompatibilidade ou
entrada/saída inválida. A mensagem informa a distinção, e somente incompatibilidade
estrutural válida produz relatório com issues. Arquivo existente não é sobrescrito.

A leitura limita a entrada a 2 MiB; o relatório a 4 MiB. O relatório contém o caso e
as expectativas completos para revalidação; **mantenha-o privado e não envie ao
modelo**. O script não abre assets, não importa adapters de modelo, não cria
provider, não chama rede nem consome orçamento. O conteúdo do projeto é sempre dado.

O relatório recalcula status, issues e hashes do caso/input. execution_authorized
é sempre false, semantic_status/model_qualification são not-established e compilação
não é autorizada. Não executa geração mesmo quando há aprovação no caso.

## Migração sem alterar o histórico

Um caso v2 destinado a v4 recebe explicit-case-migration-required. Não converter
sua antiga recusa em um escopo novo nem copiar sua aprovação. Curar um caso v3
separado e submeter expectativas/snapshot próprios à revisão humana. Para alvo v3,
requisitos fora de critérios e rejeição de conteúdo isolada são incompatíveis.

Os JSON Schemas novos são semantic-analysis-proposal-v4, semantic-analysis-v4,
semantic-assessment-case-v3 e semantic-preflight-report, em schemas/. O exportador
inclui o catálogo offline e impede colisão com os nomes históricos. CLI factory,
programas de prompts, requests e claims históricos continuam intactos.

O incremento seguinte conecta gerador v4, auditor v5, revisão/assessment v4 e runner
injetado opt-in; veja [operação e limites](semantic-v4-flow.md) e
[ADR-0031](../adr/0031-semantic-v4-injected-flow.md). Não há novas medições de modelo.
Inferência real ainda exige transporte supervisionado, fontes congeladas e novo
protocolo/orçamento explícito. Nenhum resultado reservado foi reavaliado em v4.
