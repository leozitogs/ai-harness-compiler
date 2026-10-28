# ADR-0034 — Geração v4.1 explícita, preservando programas e avaliações anteriores

Estado: candidato implementado; testes offline e CI descritos na entrega.
Eficácia com modelo real ainda não observada.

## Problema e hipótese

O PO confirmou dois casos reprovados da campanha v4: três obrigações de regra
foram representadas como requisitos e uma pergunta sobre o responsável ganhou
impacto bloqueante indevido. Os textos estavam presentes. O mecanismo de falha
de cobertura é conhecido; a causa da escolha do modelo não está demonstrada.

Hipótese de trabalho: tornar mais explícita a distinção entre obrigação
incondicional e relação que restringe/permite uma ação, assim como entre
identificação do titular de um papel e indefinição material da regra, pode
melhorar a geração. A hipótese precisa de avaliação; não corrige respostas antigas.

## Decisão

Adicionar o programa confiável `semantic-composition/v4.1`, selecionado por hash,
mantendo v4.0 como padrão e preservando suas instruções, schema e digest. v4.1
acrescenta orientação geral de representação relacional e materialidade, sem
IDs de casos, nichos, rubrica, expectativas ou respostas de referência.

Relações de condição necessária, permissão por ator, visibilidade exclusiva e
ordem temporal devem preservar componentes tipados de `business-rule` na proposta
(projetados como `rule` na análise). Obrigações incondicionais continuam em
`requirement`, sem gatilhos inventados. Uma condição necessária não vira
autorização suficiente; nenhuma permissão adicional é gerada pelo compilador.

Papéis podem permanecer simbólicos na análise de intenção. O titular desconhecido
não bloqueia por si só; dependências materiais ou alocações incompatíveis
explicitadas pelas fontes continuam exigindo perguntas. Não esconder conflitos,
indefinições de resultado ou limites de assets para produzir ready.

## Contrato e integração

`SemanticFlowRequest/v4` já possui `generation_program_sha256`. Seu catálogo passa
a aceitar hashes recalculados dos dois programas conhecidos para o schema da
entrada. Não há campos novos, alteração de formato ou migração de requests.
O digest do programa identifica instruções/schema; o pedido e os débitos vinculam
também os dados exatos da entrada. Um consumidor antigo pode rejeitar v4.1 como
programa desconhecido; deve continuar recusando-o, nunca substituí-lo por v4.0.

O registro é código confiável e fechado. Não aceita prompt arbitrário, fallback
ou revisão escolhida pelo modelo. Flow runner, supervisão e replay da campanha
resolvem o mesmo hash. Cada campanha exige uma versão uniforme de geração para
não misturar candidatos silenciosamente. O preparador tem seleção explícita
`--generation-program`; omitir a opção mantém v4.0.

O schema de saída `SemanticAnalysisProposal/v4`, sua projeção, auditoria v5,
rubrica, expectativas e políticas de autorização permanecem os mesmos. Os schemas
foram regenerados/verificados; a ampliação do catálogo de programas não muda os
campos JSON dos contratos. Não muda o principal operacional nem promove defaults.

Não há sanitização semântica pós-geração. Se o modelo emitir pergunta bloqueante,
requisito no lugar de regra ou relação sem suporte, o artefato e as falhas devem
ser preservados. Testes sintéticos verificam essa propriedade e os caminhos de
dispatch/replay; não são demonstração de melhora do modelo.

## Histórico e avaliação

Antes de modificar fontes, o candidato e os oito julgamentos anteriores foram
preservados em replay privado congelado. Os cinco arquivos históricos alterados
pela integração têm cópias públicas de bytes exatos, endereçadas por hash, no
arquivo de fontes da campanha anterior. Os testes conferem esses bytes contra o
pedido original. Novos arquivos não são apresentados como parte de uma execução
histórica. O gate de execução atual continua rejeitando o pedido antigo com
fontes diferentes; o arquivo histórico não é uma exceção de autorização.

O novo candidato precisa de pedido e orçamento próprios, com fontes atuais e
programa explícito. Usar os mesmos oito casos públicos aprovados como
desenvolvimento, incluindo os seis que passaram como regressão; não são holdout.
Não enviar expectativas à geração/auditoria nem transferir julgamentos para novos
outputs. Uma nova rodada dessa hipótese conjunta não isola causalidade de cada
frase do prompt. Comparação descritiva não qualifica o modelo automaticamente.

`INC-0031` permanece sem resolução comprovada. Não há treino, leitura de assets,
avaliação reservada, autorização de compilação ou encerramento da Sprint 2.6.
