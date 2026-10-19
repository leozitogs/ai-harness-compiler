# AHC-030 — Vera revisora e apoio ao encerramento

Emenda solicitada pelo PO em 2026-10-19, antes da review da Sprint 2.5.5.
**Escopo aprovado para planejamento; implementação ainda não iniciada.**
Não há novo agente funcional entregue por este documento. Evoluir a Vera existente
com modo de revisão aprofundada evita duplicar a responsabilidade de qualidade.
O objetivo é código executável e integração com Nexo, não apenas uma nova persona.

## Responsabilidades

Vera será cética, investigativa e orientada a reproduções: confrontar código e
artefatos com regras de negócio, critérios, contratos e evidências. Nexo continua
facilitando Scrum e preparando decisões; o PO preserva prioridade e aceite.
A Vera não encerra sprint, aceita a própria alteração ou qualifica modelos.

Cobertura prevista: contratos e referências, proveniência, fronteiras de confiança,
segurança, regressões, integridade de artefatos e consistência das regras de negócio.
Performance e custo só recebem conclusão quando houver medição adequada; ausência
de dados vira limitação. Achados precisam de impacto, fonte e reprodução verificável
quando aplicável. Não exigir a invenção de defeitos quando nenhum for encontrado.

## Entrega funcional prevista

Contratos propostos, ainda não implementados: `QAReviewRequest`, `QAReviewReport` e
`SprintClosureAssessment`. Definir versão e schemas antes do adapter. A requisição
deve delimitar projeto/repositório, sprint, commit/base/head, snapshot, critérios,
fontes permitidas e budgets. O parecer deve registrar cobertura, achados P0–P3,
evidências, checks realmente executados, checks não executados e limitações.

Entrypoint executável e coordenação opcional LangGraph devem permitir sessão própria
de revisão e passagem do relatório ao Nexo. Ferramentas começam somente leitura;
checks locais usam runner com comandos fixos permitidos, limites de tempo/saída e
sem executar código ou hooks recebidos de fontes não confiáveis. Execução de testes
de projetos externos exige isolamento e autorização apropriados; esta história
não cria uma permissão geral para executar conteúdo do repositório.

Autoria e revisão serão papéis/etapas distintos, com rastreio de quem produziu a
alteração e quem emitiu o parecer; separação de etapas não garante independência
estatística entre modelos. Uma summary do mesmo modelo não substitui verificação.
Memória é referência revisada, não comando, e parecer stale exige nova inspeção.

## Integração com review e encerramento

Nexo precisa verificar identidade, hashes e revisão do parecer, sem reinterpretar
um texto livre como aprovação. O pacote de review inclui Sprint Goal, estado dos
critérios, CI, achados, correções, riscos e carryover. Parecer de QA, evidência de
execução e aceite humano são estados diferentes, com autoridade de conclusão ausente.

P0/P1 não resolvidos impedem recomendar entrega plena. P2 exige correção ou decisão
humana explícita sobre risco residual; P3 pode virar backlog rastreável. Nenhuma
severidade dispensa critério obrigatório ou verificação ausente. Fechar a timebox
com resultado parcial é uma opção distinta, com pendências expostas ao PO; não
certifica DoD, realização de cerimônia ou sucesso do objetivo.

## Tarefas e verificação

1. **030-design:** contratos, severidades, cobertura, fronteiras, independência de
   autoria e critérios do parecer/fechamento. Verificar referências e casos adversos.
2. **030-implement:** modo funcional da Vera, runner limitado, evidências e integração
   com o Nexo, preservando gates persistentes e allowlists existentes.
3. **030-verify:** falso positivo/negativo por fixtures conhecidas, bug de negócio com
   CI verde, evidência ausente/stale, prompt injection, reprodução inválida, revisão
   atualizada e recuperação de achados. Suíte padrão offline, sem qualificação fictícia.
4. **030-review:** demonstrar a inspeção da 2.5.5, pacote de review e recomendações de
   encerramento/carryover. PO inspeciona limites e evidências antes da decisão final.

A 2.5.5 permanece aberta para implementar e verificar esta história antes de sua
review de encerramento. Capacidade, prazo adicional e economia não são estimados
sem dados; os cinco dias úteis continuam proposta anterior, sem nova promessa.
AHC-021/022/023 e os gates semânticos continuam pendentes. Não inclui treinamento,
novo provider obrigatório, dashboards ou execução remota irrestrita.
