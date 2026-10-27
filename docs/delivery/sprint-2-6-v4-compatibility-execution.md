# Sprint 2.6 — resultado da rodada de compatibilidade v4/v5

Data: 2026-10-27. Rodada encerrada com falha; orçamento consumido e fechado.

O PO autorizou explicitamente o request
`2e8963f18cb88f2dc7d70e737a0bafe8872b822a149c6f1985c66e48ae2f60cd`,
respondendo “Autorizo esta única rodada nesses limites”. O runner congelado
executou uma única vez, sem alterar o caso, programas, fontes ou limites.
Os arquivos da proposta e do pedido revisado continuam como snapshots históricos.

| Observação | Resultado |
| --- | --- |
| Rodada | `compat-v4-catalog-20261027-02` |
| Destino/modelo solicitado | Assinatura ChatGPT/Codex CLI; `gpt-6.1-sol` |
| Invocações debitadas | Uma, da etapa de análise |
| Etapa de auditoria | Não chamada, por parada na primeira falha técnica |
| Resultado do transporte | `failed`, código `invalid-output` |
| Resultado do fluxo | `failed`, código `analysis-failed` |
| Tempo do worker / sessão | 22,0610s / 22,4728s |
| Contenção e encerramento | Windows Job Object; raiz encerrada e coletada; exit code zero |
| Integridade | Replay verificado com fontes originais congeladas |
| Análise aceita / auditoria | Nenhum artefato de análise aceito; nenhuma auditoria |
| Orçamento | Fechado; a segunda invocação não vira crédito para outra rodada |

O [registro público de metadados](../evidence/sprint-2-6-v4-compatibility-execution-20261027/execution.json)
vincula autorização, hash do relatório privado, recibo e limites. Os journals e
o relatório integral permanecem privados em `.factory/`. Não houve retry, repair,
fallback, retomada ou segunda rodada. As reproduções descritas abaixo usam apenas
providers sintéticos locais e não consomem chamadas reais.

## Diagnóstico offline e limite da conclusão

O worker original escrevia `json.dumps(..., ensure_ascii=False)` em
`sys.stdout`, uma interface de texto. Neste host, o processo Python isolado com
saída redirecionada informou encoding `cp1252` e UTF-8 mode desativado. O supervisor
recebe bytes e os interpreta como JSON, cujo caminho normal espera UTF-8.

Com o mesmo worker e um provider sintético, a resposta literal `ação` gerou exit
code zero e 36 bytes que não formavam JSON UTF-8 válido. Decodificar esses bytes
como cp1252 recuperou exatamente o valor sintético original. O novo teste
`latin-cp1252` reprovou antes da correção. A
[reprodução preservada](../evidence/sprint-2-6-v4-compatibility-execution-20261027/encoding-reproduction.json)
demonstra um defeito concreto na fronteira de bytes, compatível com o código de
falha observado na rodada real.

Os bytes inválidos da rodada real não foram retidos pela política do supervisor.
Não podemos afirmar que aquela resposta tinha exclusivamente esse defeito, que
o provedor aceitou o schema ou que seu conteúdo era semanticamente correto.
Nenhuma resposta real foi recuperada, reinterpretada ou reparada.

## Correção e verificação

O worker agora escreve o envelope JSON como bytes UTF-8 explícitos em
`sys.stdout.buffer`, independentemente do encoding da interface de texto.
Não adicionamos decodificação permissiva ao supervisor nem reduzimos validações.
Os limites, gates, política de privacidade e comportamento de parada permanecem.

Seis novos testes executam o worker real com provider sintético: português e texto
com japonês/emoji, combinados com interfaces configuradas como cp1252, ASCII e
UTF-8. Cada teste exige conteúdo e hash preservados, além de encerramento observado.
Os 42 testes de transporte passaram após a correção; a reprovação anterior continua
registrada, separada da suíte normal.

Como o fonte do worker mudou, o request antigo não pode executar com o código
corrigido. O replay histórico foi preservado e verificado em uma cópia privada das
fontes e journals originais, sem inferência. Não alteramos hashes antigos para
fazê-los corresponder ao novo código. Uma nova observação no provedor exigirá outro
request congelado e autorização específica; não foi preparada ou executada aqui.

| Próximo trabalho | Dependência | Verificação |
| --- | --- | --- |
| Integrar correção | Regressões e checks | Suíte completa, fontes históricas preservadas e CI verde |
| Preparar nova compatibilidade | Correção integrada | Novo freeze do worker; caso aprovado preservado; orçamento próprio |
| Observar provedor | Novo request autorizado | Novos recibos e resultados, sem transportar o orçamento encerrado |
| Julgar conteúdo | Nova análise aceita | Revisão humana dos seis critérios, separada do parecer do auditor |

A compatibilidade do provedor continua **não estabelecida**. Não há julgamento
semântico possível de uma análise inexistente, qualificação do modelo, promoção
de default, autorização de compilação ou conclusão da Sprint 2.6.
