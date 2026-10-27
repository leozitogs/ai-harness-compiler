# Integração experimental v4: análise, auditoria e revisão

O fluxo é funcional com gerador JSON injetado, sem provider ou comando de inferência
padrão. Não altera factory, receitas históricas, defaults ou resultados reservados.
Fundamento e limites: [ADR-0031](../adr/0031-semantic-v4-injected-flow.md).

## Plano executável e verificação

| Etapa | Dependência | Verificação |
| --- | --- | --- |
| Inventário comum | SemanticAnalysis/v4 | Componentes, fontes e hashes independentes |
| Geração v4 | Extração literal e schema dinâmico | Somente projeto no payload; resposta inválida encerra |
| Auditoria v5 | Análise validada e inventário | Cobertura exata; componente negativo não admite agregado positivo |
| Revisão/assessment v4 | Caso v3, rubrica v2 e análise | Aprovações não transferíveis; todos os critérios; falhas acumuladas |
| Runner injetado | Pedido exato, autorização e preflight | Fábrica após gates; duas invocações sequenciais; primeiro erro encerra |
| Replay e revisão persistida | Journal privado e resultado | Detectar adulteração; arquivo novo; sem chamar modelo |
| Integração | Regressões e schemas novos | Checks completos, memória atualizada e PR |

## Interfaces

`semantic_generation_v4.analyze_v4(extraction, generator)` gera análise;
`audit_v5(analysis, generator, requested_model)` gera parecer consultivo.
O protocolo JSONGenerator expõe `generate_json(prompt, schema) -> str`.
Não há fábrica de provedor, credencial, rede ou adapter selecionado neste módulo.
JSON Schema dinâmico restringe IDs/fontes; validação host permanece obrigatória.
Compatibilidade com um provedor real ainda não foi medida.

`assess_v4(case, rubric, analysis, review=None)` separa falhas determinísticas
e julgamentos humanos. Sem revisão, critérios restantes ficam not-run. Um parecer
do modelo não é SemanticHumanReview/v4. Uma aprovação humana é sempre vinculada
ao novo snapshot; aprovação de expectativas ou execução não aprova saída.

`run_semantic_flow_v4(repository, request, authorization, generator_factory)`
recebe SemanticFlowRequest/v4 e SemanticFlowAuthorization/v4 explicitamente.
O pedido vincula caso v3, rubrica v2, modelo solicitado e programas por digest.
Não gerar autorização a partir de resultados de modelo ou antigos aceites.

Artefatos ficam em `.factory/semantic-v4-runs/<run_id>/`; claims ficam em
`.factory/semantic-v4-claims/<request-sha256>.json`. Pedido, expectativas,
fontes, respostas e revisões são privados. Não publicar esses arquivos. Prompts
enviados são representados somente por SHA256; mensagens de exceção de provider
não são persistidas. O journal registra débito antes de cada chamada. Respostas
finais JSON são salvas, não raciocínio privado. Saídas existentes não são sobrescritas.

`validate_semantic_flow_v4(repository, run_id)` verifica resultado, claim,
artefatos, respostas e hashes exatos dos prompts/schemas reconstruídos offline.
É integridade local, sem assinatura criptográfica contra substituição integral
do conjunto por alguém com acesso de escrita ao repositório.

`save_semantic_review_v4(repository, run_id, review)` valida o journal antes de
salvar novo assessment humano por digest; o resultado inicial permanece intacto.
Completed indica somente duas etapas técnicas validadas. Mesmo um assessment
humano pass mantém model_qualification=not-established e compilation_eligibility=
not-authorized. Não existe promoção automática ou execução de artefato gerado.

## Antes da próxima rodada real

Existe agora um [transporte opt-in supervisionado](supervised-v4-transport.md),
testado com subprocessos locais sintéticos. Ainda é necessário congelar o pedido
concreto e aprovar novo protocolo e orçamento antes de inferência real. As duas invocações
injetadas não limitam requisições escondidas em um transporte arbitrário nem
interrompem uma chamada bloqueada. Não usar este runner como supervisor de
produção. Curadoria independente e revisão humana de expectativas novas continuam
necessárias para outro reservado; o corpus já exposto permanece histórico.
