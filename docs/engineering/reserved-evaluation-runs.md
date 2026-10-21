# Execução reservada e avaliação humana

Este fluxo acrescenta uma fronteira explícita à preparação de ADR-0028. Código e
testes sintéticos não autorizam ler ou executar o corpus real. O PO já aprovou as
oito expectativas; o aceite está vinculado ao corpus original e não foi copiado
para os casos ou transferido para respostas ainda não geradas.

## Plano de execução e verificação

| Etapa | Dependência | Verificação |
| --- | --- | --- |
| Congelar pedido | Expectativas aprovadas e candidato congelado | Perfil e fontes selecionadas coincidem com os digests anteriores; orçamento exato por slot; novos hashes do executor |
| Preparar metadados | Pedido tipado | CLI não abre casos nem cria provider; saída nova informa autorização pendente |
| Registrar autorização | PO decide conteúdo, destino, limites e digest concreto | Declaração humana distinta de produtores, sem reutilizar o aceite das expectativas |
| Consumir e verificar | Autorização válida | Claim exclusivo, fontes reais conferidas, todos os bytes/contratos privados conferidos antes da primeira chamada |
| Executar sequencialmente | Preflight completo | Um débito por invocação; análise antes da auditoria; parada na primeira falha; slots restantes `not-run` |
| Reproduzir evidência | Resultados persistidos | Hashes, recibos e artefatos reconstruídos de respostas finais salvas; zero chamadas |
| Julgar saídas | Evidência íntegra e análise válida | Nova revisão humana dos seis critérios, obrigações, findings e componentes; sem autoaceite do auditor |

## Comandos

```sh
factory prepare-reserved-run request.json --repository . --output .factory/new-preparation.json
factory run-reserved-evaluation request.json --repository . --authorization authorization.json
factory validate-reserved-run .factory/reserved-v2-executions/run-id --repository .
factory assess-reserved-analysis .factory/reserved-v2-executions/run-id \
  --repository . --case-id case-id --repetition 1 \
  --review .factory/human-output-review.json \
  --output .factory/reserved-v2-executions/run-id/new-assessment.json
```

O extra `understanding` é necessário para o adapter e projeção de schema. Preparar
um pedido não produz autorização. O arquivo de autorização somente será criado
depois da decisão humana específica sobre o pedido concreto. Seu digest é o JSON
canônico do contrato completo, não o SHA dos bytes indentados. O comando de run
não aceita override de modelo, timeout, saída ou fallback por linha de comando.

O diretório precisa ser novo e estar sob `.factory/reserved-v2-executions/`.
Claim fica em `.factory/reserved-run-claims/<request-digest>.json`. Não apagar
claim para repetir, não importar o reservado v1 nem mover casos para testes/treino.
Revisão e resultados contêm dados reservados: permanecem privados e fora do pacote.
No máximo 2 MiB por artefato, 256 KiB no pedido/prompt e 32 MiB no corpus carregado.

Recibos registram intenção debitada e retorno/erro; `model_invocations_charged`
inclui falha que possa ter ocorrido antes de alcançar o serviço. Não apresentá-lo
como contagem observada de requests remotos. Custo, sampler, digest imutável e
recursos desconhecidos permanecem desconhecidos. Sem mediana ou score inventado.

## Semântica de falhas e revisão

Falha de preflight consome o pedido, salva diagnóstico e registra zero invocações
de modelo; não envia casos parcialmente conferidos. Falha de geração conserva a
resposta final disponível e impede a auditoria e slots seguintes. Nenhum erro é
repair, fallback ou aprovação. Interrupção abrupta pode deixar journal incompleto:
reconciliar antes de qualquer nova decisão, sem supor execução inexistente.

Replay não executa código gerado nem usa provider. Verifica ligação de resposta,
prompt, schemas e programa, inclusive contradições com hashes internamente
coerentes. Sucesso do replay indica integridade, nunca suporte semântico.

Sem `--review`, assessment reservado permanece `not-run` ou `fail` pelos checks
determinísticos. Aprovar expectativas não aprova saída. Com revisão humana válida,
o wrapper reservado pode ser `pass` mantendo a avaliação v3 interna `not-run`, pois
o campo inline original continua nulo. Isso é resolução explícita de autoridade
externa, sem alterar hashes históricos. Um pass de caso não qualifica o modelo,
autoriza compilação ou conclui AHC-021/022/Sprint 2.6.

Arquitetura e limites: [ADR-0029](../adr/0029-single-use-reserved-execution.md).
