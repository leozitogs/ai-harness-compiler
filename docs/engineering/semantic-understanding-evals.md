# AHC-021 — Corpus e avaliação de artefatos

Primeiro incremento funcional: corpus v1, contratos de rubrica/revisão/relatório e
runner offline. Ele avalia uma proposta salva contra um caso congelado. Não executa
LLM, não qualifica modelo e não aplica entendimento ao harness.

## Corpus congelado

`evals/understanding/v1` contém `rubric.json`, `development.json`, `holdout.json` e
`freeze.json`. O freeze verifica bytes dos três artefatos. Cada split tem 8 casos
distintos, sem IDs de caso/projeto ou conteúdo de projeto compartilhado entre splits
(a verificação de clones ignora id/name, sem alterar o digest canônico do input):
domínio novo, regras A/B, conflito branding/backlog, ambiguidade, regras compatíveis,
asset não lido e input adversarial. Exemplos são dados; não há nichos no core.

O caso `dev-compatible-rules` preserva o input público Learning Studio para avaliar
as saídas reais já registradas. Holdout tem projetos/textos diferentes e não deve
ser usado para otimização. Expectativas e thresholds ainda requerem revisão do PO;
freeze não significa aprovação. Mudanças exigem nova versão/diretório/manifesto,
revisão e evidência; não editar v1 para acomodar um resultado.

Este holdout é sintético e foi criado na mesma sessão de engenharia; não foi
curado/cegado por um avaliador independente. Separação e freeze impedem mudanças
silenciosas, mas não provam representatividade ou ausência de viés de autoria.

## Critérios

Rubrica fixa seis dimensões: cobertura de regras, suporte de citações, validade de
conflitos, limites de assets, incerteza e entendimento do projeto. `ExpectedRule`
vincula quote e pointer ao input original. Não gera condição/resultado correto
automaticamente a partir dessa quote; o revisor decide seu significado.

Achados automáticos neste incremento: ausência de todas as BusinessRule quando
há regras obrigatórias, conflito formal em caso que não espera conflito, ausência
do conflito esperado e falta de pergunta bloqueante requerida. Se existem regras,
o algoritmo não assume que elas cobrem as obrigatórias: esse julgamento é humano.
Conflitos embutidos em statements e conteúdo de assets exigem leitura semântica.

`SemanticReview` exige os seis julgamentos e hashes de caso/rubrica/proposta.
Cobertura aprovada mapeia toda regra obrigatória a uma BusinessRule que cita a
fonte correspondente. Suporte aprovado exige julgamento de cada item, preservando
seus source_refs. Declarações, hipóteses, condições/resultados, conflitos e perguntas
devem ser revisados; IDs existentes não provam suporte semântico.

## Estados e limites

- `fail`: achado automático ou julgamento humano negativo.
- `not-run`: julgamento semântico incompleto ou rubrica sem aprovação declarada.
  Não significa que um LLM jamais gerou o artefato.
- `pass`: todos os critérios aprovados, cobertura/suporte completos e rubrica com
  aprovação declarada. É o resultado da revisão registrada, não prova de autenticação.
- `error`: artefato inválido, snapshot divergente ou revisão inválida/stale.

Status/checks/hashes contraditórios são rejeitados inclusive ao desserializar.
`execution_evidence` permanece offline/model-execution-not-established e
`model_qualification` sempre not-established. Não há scores de confiança ou
qualidade inferidos. O candidato não fornece a revisão via este runner.

Leituras limitadas a 2 MiB por arquivo; arquivos do corpus precisam resolver dentro
da pasta. Saída exclusiva, sem sobrescrever. Falha de escrita pode deixar arquivo
parcial. Freeze/revisor são declarados, não assinatura/auth; o opt-in de holdout
evita uso acidental, não autentica que o candidato realmente foi congelado.

## Uso

```sh
factory eval-understanding docs/evidence/sprint-2-5-ac-pilot/cold-understanding.json \
  --corpus evals/understanding/v1 --case dev-compatible-rules --output evaluation-new.json
factory validate-eval-report evaluation-new.json --corpus evals/understanding/v1
```

`eval-understanding` grava inclusive fail/error/not-run e retorna exit 1 nesses
estados; exit 0 somente para pass. `validate-eval-report` retorna exit 0 quando o
relatório é consistente com seu corpus, inclusive se seu resultado for fail.
Validação de relatório não altera seu resultado.

Revisão opcional em arquivo separado: `--review review.json`; schema disponível em
`factory schema semantic-review`. Para holdout, `--split holdout --allow-holdout
--candidate-sha256 SHA256` exige declaração explícita. Não avaliar holdout para
ajustar prompt; pipeline/candidato precisa ser congelado previamente.

## Evidência e próximos passos

Três artefatos públicos anteriores (Qwen3.5, Qwen3 cold/warm) foram avaliados sem
nova chamada de modelo. Todos falharam por ausência de BusinessRule; Qwen3.5 também
falhou por conflito formal incompatível com a expectativa. Outros critérios
continuam not-run. Relatórios em `docs/evidence/ahc-021/` preservam esse resultado.

Pendentes: revisão do PO sobre rubrica/corpus, runner de geração real e budgets de
sessão, metadados correlacionados de modelo/execução, pipeline/prompt da AHC-022 e
qualificação AHC-023. INC-0007 não foi resolvido. Não executar o holdout antes desse
gate nem declarar AHC-021 Done por este primeiro incremento.

Incremento posterior: [runner de sessões de geração](model-generation-sessions.md)
implementa supervisão, budgets e metadados. O formato offline descrito aqui permanece
compatível; revisão da rubrica, grounding e qualificação continuam pendentes.
