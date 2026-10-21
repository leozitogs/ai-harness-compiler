# Sprint 2.6 — Diagnóstico estrutural das avaliações reservadas

## Plano executável desta continuação

| Tarefa | Dependência | Verificação |
| --- | --- | --- |
| Conferir rodada e contratos | Replay dos artefatos preservados | Nenhuma chamada; fonte e snapshot exatos |
| Enumerar causas estruturais | Inventário de obrigações/findings | Não sobrescrever achados do mesmo critério |
| Reproduzir em inputs sintéticos | Projeção v3 e avaliador públicos | Texto literal presente pode continuar sem representação requirement |
| Entregar diagnóstico offline | Reprodução e invariantes | Snapshot errado rejeitado, saída existente preservada, sem promoção |
| Solicitar julgamentos pontuais | Fontes e saídas privadas preservadas | Decisões do PO separadas de pareceres e expectativas históricas |
| Planejar migração | Diagnóstico e julgamentos | Novo contrato/protocolo separado; nenhuma reavaliação retroativa |

## O que a inspeção demonstrou

O inventário tem **41 obrigações**, das quais **18 não encontram finding com o
kind e a fonte exigidos**. Em 17 delas, o kind exigido é `requirement`, mas a fonte
não é um critério de aceitação. Isso não pode ser expresso pela projeção v3:
`criterion` produz requirement ancorado no próprio critério; contexto produz
statement/domain; guard produz rule; issue produz question/conflict/rejection.
Trocar o átomo do critério pelo átomo de contexto é rejeitado pelo contrato.
Não é uma deficiência que outra temperatura ou novo prompt possa resolver.

As 18 obrigações não correspondidas têm candidatos citando o mesmo pointer.
**Coincidência de fonte não prova cobertura semântica.** Texto pode ter sido
resumido incompletamente ou interpretado incorretamente. Nos testes sintéticos,
a cópia literal de concepção, descrição e restrição ainda falha na identidade de
kind; no reservado não atribuímos automaticamente correção semântica a esses
candidatos. A 18ª obrigação é uma diferença requirement/rule dentro de um
critério, tecnicamente representável e ainda sujeita a julgamento específico.

Portanto, os oito FAIL históricos de cobertura misturam pelo menos uma exigência
inexpressável por caso com possíveis problemas adicionais. Não equivalem a uma
medição válida de oito falhas semânticas independentes do modelo. Não transformamos
nenhum deles em PASS nem removemos as expectativas que o PO aprovou.

O inventário também identifica **duas divergências de disposição**, uma ausência
de recusa explícita e nenhuma ausência estrutural de conflito exigido. O relato
anterior contou uma divergência porque `_derived_checks` mantém só uma mensagem
por critério: a mensagem da recusa substituiu a divergência no mesmo caso. O
status fail permaneceu correto segundo o contrato original, mas a enumeração de
causas era incompleta. O diagnóstico novo enumera os dois fatos sem sobrescrita.

## Implementação e limites

`case_diagnostics.diagnose_case` é uma transformação pura, sem provider ou I/O.
Recebe os contratos existentes, revalida-os, confere o digest de projeto e retorna
projeções internas tipadas e imutáveis com hashes, candidatos por pointer,
correspondências estruturais, representabilidade limitada, disposição, recusa e
conflito. Não decide significado nem aceita uma equivalência de tipos.

`scripts/diagnose_semantic_case.py` é a fronteira opt-in de arquivos limitados e
saída nova. Exemplo somente com arquivos já autorizados:

```sh
python scripts/diagnose_semantic_case.py --case case.json --analysis analysis.json --output new-diagnostic.json
```

Essas dataclasses são projeções internas, não contratos de aprovação versionados.
Os modelos, schemas, prompts, defaults e fontes congeladas do executor/candidato
permanecem iguais. Os JSON Schemas existentes continuam sendo verificados.
Treze testes sintéticos exercitam a incompatibilidade, a preservação dos dois
achados simultâneos, materialidade de perguntas, conflitos, rejeições, vínculos e
proteção contra sobrescrita. Foram escritos após o diagnóstico: são regressões
de invariantes de software, **não** validação cega independente de um novo modelo.

## Decisões de negócio pendentes

Duas perguntas específicas foram apresentadas ao PO no dossiê privado
`causal-review/business-questions.md`: materialidade de uma pergunta bloqueante e
tratamento da instrução maliciosa sem registro explícito da rejeição. Pareceres
continuam consultivos até resposta. Esses julgamentos não preenchem os seis
critérios de cada saída e não apagam os FAIL determinísticos.

## Esteira de resolução

1. Revisar as obrigações semanticamente e distinguir preservação, omissão e
   representação. Manter os snapshots, julgamentos e expectativas originais.
2. Projetar **separadamente** um contrato novo que permita tipar requisitos de
   contexto e distinguir rejeição de um trecho não confiável da disposição do
   projeto. Não tratar statement como requirement por mera coincidência de fonte.
3. Definir regras de cobertura com identidade semântica, proveniência e força
   normativa; adicionar preflight de representabilidade antes de gastar orçamento.
   Congelar novos schemas/ADRs e protocolo, preservando compatibilidade histórica.
4. Reproduzir correções em desenvolvimento; qualquer novo candidato deve ser
   congelado antes de outro reservado independente e de sua revisão humana.
   Os casos agora inspecionados não podem fundamentar nova alegação de generalização.
5. Somente após gates, medir qualidade, custo e latência e considerar promoção.
   AHC-024/025/026 seguem seus critérios; treinamento e inferências não foram autorizados.

O pacote privado preserva diagnósticos vinculados aos oito pares de snapshots.
O resumo público contém apenas metadados operacionais. O responsável pelo
candidato já inspecionou estrutura e alguns textos depois da execução: essa
exposição está registrada e impede tratar o mesmo corpus como avaliação cega nova.
Sprint 2.6 permanece aberta. Nenhuma história, modelo ou compilação foi aprovado.

## Atualização posterior — dois julgamentos específicos recebidos

O PO confirmou “Confirmo: bloqueio indevido” para a pergunta de materialidade de
c-d903f6a2 e “Confirmo a interpretação limitada” para a ausência de registro
explícito da rejeição em c-f61b902c. O primeiro julgamento rejeita aquele bloqueio;
o segundo reconhece falha de rastreabilidade sem concluir obediência ao ataque
e preserva a análise legítima. São decisões vinculadas aos snapshots no registro
público redigido `scoped-business-decisions.json` e no recibo privado correspondente.

As perguntas deixaram de estar pendentes, mas não foi emitido um
SemanticHumanReview/v3 completo. Não há aprovação dos seis critérios, das
respostas inteiras, de um novo contrato ou de nova rodada. Corpus, expectativas,
disposições e assessments históricos continuam intactos. A etapa seguinte é
projetar a migração de contrato com essas decisões explícitas, preservando
proveniência, cobertura e o resultado reprovado observado.
