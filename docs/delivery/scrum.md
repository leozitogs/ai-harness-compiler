# Acordo de trabalho inspirado no Scrum

O [Scrum Guide](https://scrumguides.org/scrum-guide.html) é a referência do framework.
Scrum envolve Product Owner, Scrum Master e Developers, com Product Backlog,
Sprint Backlog e Increment. Product Goal, Sprint Goal e Definition of Done dão
compromisso a esses artefatos. A equipe precisa confirmar as responsabilidades.

## Adaptação inicial deste projeto

Propomos sprints de dez dias úteis. Planning seleciona um objetivo viável,
Daily inspeciona avanço e impedimentos, Review coleta feedback sobre o incremento,
e Retrospective escolhe uma melhoria do processo. Refinamento ocorre ao longo da sprint.
Datas e duração das reuniões serão acordadas no kickoff; não há eventos agendados.

Convenções locais: Planning de até 90 minutos, Daily de até 15 minutos, Review
de 45 minutos e Retrospective de 30 minutos para a equipe inicial. Esses tempos
são uma proposta operacional, não limites obrigatórios universais do Scrum.

## Definition of Ready — convenção local

Objetivo compreendido; critérios testáveis; dependências conhecidas; riscos e
dados identificados; história cabe na capacidade prevista; estratégia de verificação
discutida. Ready é uma prática local e não um artefato obrigatório do Scrum.

## Definition of Done

1. Critérios de aceitação atendidos com evidência identificável.
2. Testes relevantes e todos os checks obrigatórios da CI aprovados.
3. Revisão concluída, comentários resolvidos e branch integrada pelo fluxo definido.
4. Schemas, documentação, plano e ADRs atualizados quando afetados.
5. Compatibilidade, segurança, licenças e falhas relevantes avaliadas.
6. Nenhuma declaração fictícia de eval aprovado ou funcionalidade executada.

Um plano gerado, código em branch ou PR aberto não é um Increment Done. Trabalho
incompleto retorna à ordenação do backlog, sem manipular pontos para parecer entregue.

## Capacidade, WIP e mudanças

Começar com uma história ativa por developer e até uma aguardando review como
limite experimental. Pontos são estimativas relativas, opcionais e calibradas pela
equipe; sem velocity histórica, não prever produtividade. Medir lead time,
retrabalho, bloqueios, defeitos e alcance do Sprint Goal antes de automatizar métricas.

O plano pode ser adaptado conforme aprendizado, preservando o Sprint Goal e a
qualidade. Escopo adicional exige renegociação, não inclusão silenciosa de trabalho.
TaskGraph indica precedência técnica; não agenda pessoas nem promete paralelismo real.
