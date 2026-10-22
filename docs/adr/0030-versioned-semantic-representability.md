# ADR-0030 — Representabilidade semântica e rejeição por escopo

Estado: implementado como contratos e ferramenta offline em 22/10/2026.
Sem integração ao gerador ou aprovação semântica. Complementa ADR-0021/0029.

## Problema

A representação v3 só produz requirements a partir de critérios de aceitação.
Concepção, descrição e restrições viram statement/domain, enquanto AssessmentCase/v2
permite exigir requirement nessas mesmas fontes. Há expectativas válidas de fonte
literal mas impossíveis para a representação alvo. Rejeitar qualquer trecho em v3
também força safely-rejected para todo o projeto, conflando a instrução não confiável
com o restante da proposta legítima. INC-0027 documenta o diagnóstico histórico.

## Decisão

Adicionar SemanticAnalysisProposal/v4, SemanticAnalysis/v4, AssessmentCase/v3 e
SemanticPreflightReport/v1, sem modificar as versões antigas ou converter suas
aprovações. Requisitos explícitos têm identidade, conteúdo, força required/prohibited
e aplicabilidade opcional, cada conteúdo com seus átomos. Ausência de aplicabilidade
não inventa gatilho nem bloqueio. Contexto factual continua factual.

A proposta contém project_analysis/v3 para preservar regras/guards/proveniência por
componente e a validação exata de critérios, além dos novos canais requirements e
content_rejections. Trata-se de composição tipada nova, não de migração automática.
Um caso novo não é produzido de um caso antigo; requer curadoria e revisão próprias.

ContentRejection/v4 registra somente instrução não confiável e não altera a
disposição do projeto. safe-rejection/untrusted-instruction é recusado no canal de
projeto novo. A rejeição histórica de projeto por unread-required-source continua
possível, separada; perguntas materiais/conflitos continuam bloqueando. Isso não
constitui uma política geral de conteúdo ou uma autorização para executar ferramentas.

AssessmentCase/v3 distingue recusa esperada de conteúdo e de projeto e permite
exigir statement/domain sem forçá-los a requisito normativo. Fontes literais,
obrigações, conflitos, disposições e limites continuam sendo validados. Nenhuma
expectativa content-rejection impõe rejeitar a proposta inteira.

O preflight recebe somente caso e versão alvo, antes de qualquer geração. Detecta
requirements de contexto inexpressáveis em v3, canal isolado de rejeição indisponível
em v3 e necessidade de migrar explicitamente um caso v2 antes de usar v4. Observações,
hashes e status são recalculados pelo contrato do relatório. compatible significa
representabilidade estrutural, sem execução autorizada, suporte semântico ou qualificação.

Os schemas novos ficam em registro offline separado, exportado pelo mesmo script
verificador. Não mudamos cli.py nem fontes do executor/candidato congelados, para
preservar o replay histórico. O comando factory schema continua expondo seu catálogo
histórico; os schemas experimentais são arquivos explícitos e contratos Python.

## Alternativas rejeitadas e limites

Não converter statement em requirement por coincidência de pointer. Não remover
expectativas para obter PASS. Não reinterpretar safely-rejected de um snapshot v2
como rejeição de trecho. Não testar novamente o reservado exposto nem transportar
seus julgamentos. Não vincular compatibilidade do preflight a orçamento de inferência.

O preflight é uma ferramenta opt-in offline; ainda não altera o runner histórico
nem demonstra aplicação automática antes de uma chamada real. Precisaremos de novo
protocolo/runner, gerador, auditor e avaliação/revisão v4 compatíveis, com fontes
congeladas, expectativas novas, orçamento e decisões humanas separados. Modelos e
fatos normativos continuam hipóteses interpretativas sem revisão semântica.

Os testes sintéticos de desenvolvimento verificam invariantes de engenharia, não
qualificam um modelo nem resolvem todos os critérios de INC-0027/Sprint 2.6.
