# Sprint 2.6 — Preparação do reservado v2

O PO escolheu um agente independente em contexto isolado para propor casos novos,
com revisão humana posterior. Este incremento prepara contratos, congelamento e
gates offline. Nenhuma avaliação reservada ou nova rodada de desenvolvimento foi
autorizada por essa escolha. Orçamentos anteriores continuam encerrados.

## Sequência e verificação

1. Congelar a receita candidata antes de gerar casos: commit base `1e8db614`,
   composição `semantic-composition/v3.4`, auditoria `component-audit/v4.1`, fontes
   selecionadas e configuração solicitada da assinatura Codex. O digest canônico
   do candidato está em `evals/understanding/v2/reserved-preparation/candidate.json`.
2. Curador em contexto novo elabora oito inputs sintéticos e expectativas
   `AssessmentCase/v2`, sem consultar desenvolvimento, respostas, exemplos ou
   reservado v1. Acesso limitado a código de contratos e metadados do congelamento.
   Nenhum domínio é codificado como nicho suportado. Sete cenários de avaliação,
   incluindo duas regras contrastantes, verificam generalidade e fidelidade.
3. Curador valida contratos e registra hashes; raw cases e revisão integral para
   o PO ficam em `.factory/reserved-v2-curation-20261021/`. Autor do candidato lê
   somente manifesto/proveniência, sem inputs ou expectativas. O contexto novo é
   isolamento instrucional, não controle de acesso independente de filesystem.
4. Preparar diagnóstico pelos metadados. Declarações de famílias e fingerprints
   permitem detectar sobreposições exatas; não provam independência semântica ou
   autenticidade. Casos não são abertos pelo preparador.
5. PO revisa fontes e expectativas dos oito casos; só depois registrar declaração
   vinculada ao corpus. A escolha do curador não é esse aceite. Se houver ajustes,
   curador atualiza os casos e hashes; não utilizar outputs do candidato para isso.
6. Preparar protocolo concreto de acesso/execução, perfil e orçamento para decisão
   do PO. Verificar bytes e contratos na fronteira autorizada antes de executar.
   Preservar erros e saídas originais, sem retries/repair. O runner desta etapa
   ainda não foi implementado. Preparação não consome orçamento de avaliação.
7. Julgar novas saídas nos seis critérios da rubrica congelada. Manter análise,
   auditoria consultiva, revisão humana e qualificação separados. Não otimizar no
   reservado nem promover defaults automaticamente.

## Uso offline

```sh
factory prepare-reserved-evaluation \
  evals/understanding/v2/reserved-preparation/protocol.json \
  --output .factory/reserved-preparation-new.json
```

O comando cria arquivo novo, lê no máximo 2 MiB de protocolo e retorna `1` com
diagnóstico quando há gates pendentes; retorna `0` se metadados são `reviewable`.
Ambos os estados mantêm `execution_authorized: false`, `model_calls: 0`,
`payload_validation: not-performed` e `identity_authentication: not-established`.
Os hashes são declarações até verificação dos respectivos arquivos. Os JSON
Schemas novos podem ser validados pelos comandos gerais do CLI.

Revisão vinculada ao corpus não assina identidade. Orçamento proposto não concede
permissão e não faz chamadas. Exige `2 × casos × repetições`, concorrência 1,
retry/repair 0, limites por chamada/sessão. Timeout de sessão pode interromper
antes de consumir todas as chamadas; não é promessa de conclusão.

## Entrega e pendências

O curador entregou oito casos, oito bindings e roundtrip dos contratos validados,
com aprovações nulas. O manifesto e a proveniência pública são declarações do
curador; o autor do candidato não abriu os arquivos privados para revalidá-los.
O diagnóstico registrado tem exatamente dois gates pendentes: revisão humana das
expectativas e orçamento ainda não proposto. O corpus de metadados tem digest
`c010e3373338edee86512a889ed12273c0a25ac44403e25e4c732fdbb97a8367`.
O documento privado para o PO é
`.factory/reserved-v2-curation-20261021/po-review.md`; seu hash informado pelo
curador está em `po-review-binding.json`. Nem ele nem os casos integram o Git,
testes ou pacote distribuído. O reservado v1 continua sem acesso.

Posteriormente, em 21/10/2026, o PO respondeu **“Li e aprovo as oito expectativas”**
para esse corpus. `po-expectations-review.json` registra a declaração; o novo
`protocol-reviewed.json` e `preparation-reviewed.json` deixam somente o orçamento
como gate pendente. O protocolo/diagnóstico inicial permanecem inalterados.
O exemplo de comando acima reproduz o estado inicial; use `protocol-reviewed.json`
para diagnosticar o estado posterior. Nenhum caso privado foi aberto ou alterado
pelo autor do candidato. Os campos `expectations_approval: null` originais ficam
preservados: a aprovação está no vínculo externo ao corpus. A futura fronteira
de execução/assessment precisa resolver explicitamente essa declaração, sem
reescrever hashes ou pressupor que os contratos antigos já a consumam. Não houve
autorização de execução ou julgamento de saídas.

AHC-021/022 continuam em revisão; 48 aceites humanos de desenvolvimento e o smoke
estrutural de auditoria não aceitam o reservado. AHC-024 ainda precisa consolidar
perfil e metadados desconhecidos: identidade imutável observada do modelo,
sampling efetivo, custo e recursos não foram inferidos do alias. Preparação não
resolve qualificação, comparação repetida, promoção ou fine-tuning.

Evidência deste incremento: contratos e testes em `tests/test_reserved_evaluation.py`,
congelamento e protocolo em `evals/understanding/v2/reserved-preparation/`,
diagnóstico em `docs/evidence/sprint-2-6-reserved-preparation-20261021/` e
[ADR-0028](../adr/0028-reserved-evaluation-metadata-gates.md).
