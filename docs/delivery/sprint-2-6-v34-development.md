# Rodada corretiva v3.4 — execução e revisão humana

## Resultado

Em 20/10/2026, o PO autorizou explicitamente a rodada: “autorizo, podes efetuar
a rodada.” O [evento de autorização](../evidence/sprint-2-6-v34-development-20261020/authorization.json)
vincula essa declaração ao protocolo congelado. A rejeição automática anterior
permanece como evento histórico; não houve contorno ou execução antes do aceite.

Foram executadas **16 chamadas seriais**: oito gerações válidas e sete auditorias
válidas; uma auditoria foi rejeitada pelo vínculo de hash. Não houve retries,
repair, leitura de assets, holdout, treinamento, ferramentas ou troca de provider.
Tempo observado do runner: **422,804745 segundos**. Não é benchmark cold/warm,
medida de estabilidade ou evidência causal de ganho sobre rodadas anteriores.

As oito análises mudaram de snapshot. Os assessments iniciais foram preservados
como `not-run`, com **zero reviews anteriores reutilizadas**. Posteriormente,
o PO julgou os seis critérios das oito novas análises: **8 pass, 48 critérios
pass, zero fail e zero pendentes**. Esses resultados não aprovam a auditoria
inválida, não qualificam o modelo e não autorizam compilação.

| Caso | Disposição | Auditoria | Julgamento humano da análise |
| --- | --- | --- | --- |
| dev-adversarial | ready | válida | pass |
| dev-ambiguous | blocked | válida | pass |
| dev-branding-conflict | blocked | válida | pass |
| dev-compatible-rules | ready | válida | pass |
| dev-new-domain | ready | erro de vínculo | pass |
| dev-rules-a | ready | válida | pass |
| dev-rules-b | ready | válida | pass |
| dev-unread-assets | ready | válida | pass |

## Escopo da correção semântica

Nos novos snapshots não aparece a pergunta adicional que tratava a aplicabilidade
da identidade como impedimento. A obrigação continua explícita como contexto
normativo, sem gatilho inventado ou alegação de política executável.

Em `dev-branding-conflict`, o conflito e a pergunta de precedência citam ambos os
lados e mantêm `blocked`. Em `dev-ambiguous`, a confirmação do operador continua
necessária, sem ser suficiente para concluir; a pergunta sobre condições de
conclusão bloqueia. O PO aceitou a pergunta adicional de etapas/papéis como
`implementation-detail` nesta análise de intenção, sem aprovar um workflow executável.

Nos casos `ready`, o PO aprovou preservação das regras específicas, limites de
assets, proteção contra instrução maliciosa, suporte e cobertura. Isso verifica
a resolução escopada de INC-0024 nesses oito snapshots; não prova ausência de
falhas em outros projetos ou superioridade estável da receita.

As três confirmações reais estão no
[manifesto humano](../evidence/sprint-2-6-v34-development-20261020/human-review/manifest.json).
Revisões e assessments tipados vinculam caso, rubrica, análise, achados e
componentes aos respectivos hashes. Declarações humanas não têm autenticação
independente. O [pacote completo](../reviews/sprint-2-6-v34-development/dev-ambiguous.md)
preserva inputs, saídas, fontes e pareceres consultivos, inclusive o erro.

## Falha técnica preservada

A chamada 10 devolveu uma proposta de auditoria para `dev-new-domain`, porém
alterou um caractere de `finding_sha256` em `context-4`. Os IDs de fonte coincidem;
o digest exato não. O validador rejeitou a proposta com `ValidationError`.

O [diagnóstico offline](../evidence/sprint-2-6-v34-development-20261020/execution/dev-new-domain/audit-diagnostic.json)
registra os valores esperados e observados. A resposta final original e o recibo
`returned` permanecem intactos. Retorno do provider não equivale a relatório
válido. O replay offline reproduz a rejeição sem nova chamada ou correção do hash.
INC-0025 acompanha essa falha; ela não foi apagada pelo pass humano da análise.

As sete auditorias válidas contêm dez sugestões de omissão e nenhum componente
negativo. Esses números são diagnósticos, não métricas de qualidade. Perguntas
sobre identidade e atribuição de pessoas foram avaliadas no escopo de intenção,
sem converter automaticamente cada sugestão do auditor em bloqueio.

## Evidências e próximos gates

O [inventário inicial](../evidence/sprint-2-6-v34-development-20261020/artifact-inventory.json)
contém 94 artefatos anteriores aos julgamentos posteriores. Os arquivos de
revisão humana têm seus próprios vínculos de hash no manifesto posterior.
Código/protocolo ficaram congelados em `2094624`; receitas v3.1–v3.3 e default
permanecem intactos. As regressões verificam protocolos, recibos, respostas finais,
assessments e rejeição do hash alterado sem chamadas externas.

O orçamento está **consumido e encerrado**. Nenhuma chamada foi executada durante
o julgamento humano. Não há rodada adicional automática, promoção da v3.4 ou
mudança do principal operacional. O resultado melhora a evidência de desenvolvimento;
AHC-021/022 ainda exigem revisão/DoD, e AHC-023/024/025/026 continuam pelos gates
do plano. O próximo trabalho é consolidar essa revisão e tratar o erro de vínculo
antes de alegar robustez do pipeline ou iniciar comparações de perfis autorizadas.
