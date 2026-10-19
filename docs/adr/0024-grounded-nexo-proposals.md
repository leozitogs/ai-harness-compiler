# ADR-0024 — Propostas Scrum derivadas de evidências

Status: aceito para implementação; AHC-028, 2026-10-19.

O núcleo passa de `SprintSnapshot/v1` para `ScrumPlanningReport/v1`, contendo
`ScrumActionProposal/v1`. Refinamento preserva critérios e dependências literais;
planejamento solicita capacidade aos Developers; review conserva resultado
declarado e carryover. Cada proposta liga objetivo, histórias, diagnósticos e fontes.
Alternativas são opções para discussão humana, sem comandos executáveis.

O relatório recalcula suas propostas na desserialização. Um hash consistente não
autoriza alterar critérios, destinatários, capacidade ou aceite. Não inferimos
velocidade, datas, estimativas, DoD ou aprovação a partir de lifecycle/CI.

Reutilizamos persona, allowlist, budgets, retrieval de memória revisada e checkpoint
SQLite/LangGraph existentes. `TeamRun/v1` recebe o campo opcional `scrum_snapshot`:
é extensão aditiva; configurações antigas continuam aceitas e schemas são regenerados.
Quando presente, exige projeto/seleção coincidentes e modo ask, direcionado ao Nexo
independentemente da classificação ML. Não treinamos outro classificador para uma
rota já explicitamente selecionada. O parecer opcional de LLM continua consultivo;
o conteúdo estruturado é calculado pela ferramenta, nunca pela summary do modelo.

Antes da preparação e de qualquer revisão persistente, verificamos TTL, allowlist
de caminhos, bytes atuais e equivalência do manifesto normalizado. Mudanças exigem
recoleta e nova proposta; não há atualização remota implícita. O contexto adicional
e a memória continuam sujeitos ao gate de digests existente.

Cache em memória por digest da observação evita recalcular a mesma proposta dentro
da sessão. Cada leitura revalida o snapshot; o cache guarda JSON imutável produzido por
relatório validado. Mudança de qualquer
fonte/horário/budget de freshness invalida a entrada. Escolhemos invalidação completa
para esta versão: granularidade por história e cache persistente ficam para evolução
com evidência de benefício. Não afirmamos redução de tokens ou ganho semântico.

Limites: hashes não autenticam o produtor; GitHub pode mudar após a coleta, mesmo
antes do TTL. Capacidade permanece desconhecida nesta versão, inclusive quando
campos livres do plano mencionam números. Revisão aprova somente o relatório;
operações, autorizações e recibos pertencem à AHC-029. Não certifica aceite por
critério e não resolve os gates semânticos da Sprint 2.5.
