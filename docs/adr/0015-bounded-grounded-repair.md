# ADR-0015 — Repair supervisionado com tentativas explícitas

Status: aceito para implementação estrutural; julgamento semântico pendente.

## Contexto

Os smokes da AHC-022 são rejeitados por citações, referências ou vínculos. Corrigir
somente metadados de origin para fazer passar o validador seria uma promoção falsa.
Uma nova chamada dentro do worker ocultaria retries do orçamento de tentativas.

## Decisão

Criar UnderstandingRepairPlan/Report/v1 separados do runner original: um caso de
development, uma repetição e SHA esperado do modelo obrigatório. Até duas correções
opcionais; cada chamada usa worker isolado e consome uma tentativa. Limites de
sessão, tentativa e tokens se mantêm; nenhuma alteração de profile ou aumento
automático de budget. Holdout não é admitido nesse incremento.

GroundingDiagnostic/v1 contém códigos/motivos fixos, SHA do input/proposta inválida
e IDs de evidências do snapshot original. Não contém corpo rejeitado, raciocínio
privado, texto livre de erro, IDs desconhecidos do modelo ou avaliação do próprio
candidato. Referências inválidas são diagnosticadas usando o inventário elegível
do input; citações/vínculos têm escopo validado antes do feedback.

O programa grounded-repair/v1 recebe extração e diagnóstico anterior e regenera
uma proposta completa. Pode reconsiderar classificação ou perguntar; não deve
trocar hipótese por fato apenas para satisfazer checks. Toda saída continua sujeita
aos mesmos invariantes. Schema inválido, erro do provider, fonte excluída ou outro
erro sem diagnóstico elegível encerra o fluxo sem nova chamada.

Modelo retornado é conferido antes de usar diagnósticos. Identidade observada é
conferida antes/depois também em propostas rejeitadas elegíveis para repair.
Timeout e mudança de identidade encerram o fluxo, sem próxima tentativa.

## Auditoria e compatibilidade

Gravar plan.json antes das chamadas; um attempt-NNN.json por tentativa; repair.json
por último. Saída deve ser nova. Validador cruza inventário de arquivos, plano,
corpus, request canônico, feedback anterior, resultado, programa, sequência,
tempos, orçamento e motivo de encerramento. Journals incompletos não passam.

WorkerRequest/Result ganham feedback/diagnóstico opcionais. Novos contratos são
aditivos; baseline e journals antigos continuam legíveis, com defaults ausentes.
Programa e schemas participam do hash de repair. Não migrar ou reescrever evidências.

## Limitações

Metadados do provider são observados, não autenticados. Contamos tentativas de
worker; preflight pode falhar sem chamada ao modelo. Startup, preparação, escrita
e cleanup podem exceder budgets nominais; cancelamento no servidor/GPU não é provado.
Erros não persistem a proposta rejeitada ou métricas de geração do provider.

Sem aprovação semântica automática. O smoke com duas tentativas terminou repair-limit;
esse comportamento verifica o fluxo, não melhoria de qualidade ou qualificação.
Rubrica/PO, comparação de desenvolvimento e holdout permanecem pendentes.
