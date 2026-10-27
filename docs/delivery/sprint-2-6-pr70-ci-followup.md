# Sprint 2.6 — correção da verificação de concorrência no PR #70

Data: 2026-10-27. Escopo: manutenção do teste de concorrência, sem mudança do runtime.

O primeiro commit do PR #70 (`4975309946dbb07df13bd5e55362dd74d7220b36`)
passou em quatro checks. No job Windows/Python 3.13, um teste anterior da equipe
registrou pico de uma decisão ativa, embora esperasse duas. Os 36 testes novos do
transporte passaram nesse job; o resumo foi 1.253 testes aprovados e um reprovado.

O teste usava `sleep(0.01)` para tentar criar sobreposição entre threads. Essa
espera não estabelece uma relação de sincronização: o scheduler pode executar
as chamadas sem a sobreposição esperada. A falha observada não demonstrou violação
do limite de duas chamadas pelo runtime.

A correção usa uma barreira para as duas primeiras decisões. Ambas precisam estar
ativas antes de prosseguir, com timeout de dez segundos para que uma execução
serializada falhe sem travar a suíte. As outras decisões seguem normalmente; o
teste preserva a verificação de pico igual a dois e explicita o limite observado.
Não aumentamos uma espera arbitrária nem removemos a asserção de concorrência.

Os 23 testes da equipe passaram localmente. Em um controle negativo isolado,
forçamos `max_concurrency=1` somente em memória: o teste sincronizado reprovou
como esperado. Essa reprovação intencional fica separada da suíte normal; confirma
que a correção não tornou aceitável uma execução serializada. Não alteramos o
runtime para realizar esse experimento.

| Etapa | Dependência | Verificação |
| --- | --- | --- |
| Diagnóstico | Log e commit do job reprovado | Identificar a asserção e preservar o resultado original |
| Sincronização | Diagnóstico | Duas decisões se encontram sem depender de fatia de tempo |
| Regressão | Correção | Arquivo da equipe e suíte completa offline |
| Integração | Regressões, documentação e memória | Cinco checks verdes no novo commit antes do merge |

Este teste usa decisões falsas: nenhuma chamada à assinatura ou ao modelo é
necessária. Não altera orçamento, limites do transporte, contratos, defaults,
critérios de aceite ou disposição da Sprint 2.6. Um teste sincronizado verifica
essa execução e a capacidade concorrente pretendida; não prova todas as possíveis
intercalações de threads ou desempenho de um modelo.

[Job original e evidência da falha](https://github.com/leozitogs/ai-harness-compiler/actions/runs/39869725784/job/120140823270).
