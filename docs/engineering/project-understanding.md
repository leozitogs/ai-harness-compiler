# AHC-019 — Primeiro incremento: contratos de entendimento

Implementado nesta etapa: UnderstandingRequest/v1, UnderstandingProposal/v1 e
ProjectUnderstanding/v1, schemas, preparação do snapshot e validação pela CLI.
O adapter de modelo, estudo semântico e aplicação da proposta na DNA ainda não
estão implementados. Este incremento não conclui a história AHC-019.

```sh
factory prepare-understanding project-definition
factory schema project-understanding
factory validate-understanding examples/understanding/understanding.json
```

Prepare imprime JSON, sem chamar modelo, ler assets ou acessar rede. O snapshot
é ProjectInput normalizado com defaults; seu digest segue o JSON canônico do
compilador, não os bytes originais do YAML. References apontam por RFC6901 para
concepção, branding, restrições, descrições/critérios do backlog e metadados
fornecidos. Ponteiros são seletores de dados, nunca atributos ou código executável.

References têm IDs/ponteiros únicos, project_id compatível e valor exato do snapshot.
Valores estruturados usam JSON ordenado; declarações citam texto/valor preservado.
Hipóteses podem interpretar, sempre com refs e sem confidence numérica. Domínios são
texto aberto, sem catálogo fixo. Regras registram condição, resultado, exceções e
origem; descrição extraída preserva uma citação. O contrato não prova que a condição
ou consequência é semanticamente implicada pelo texto: isso exige avaliação/revisão.

Conflitos possuem pelo menos duas refs distintas; perguntas podem bloquear revisão.
IDs são únicos em toda a proposta. Declaração inventada, ref ausente, valor alterado,
ponteiro inválido e origem de outro projeto são rejeitados. O snapshot do caller é
copiado na preparação, sem compartilhar listas mutáveis com a entrada.

## Revisão e limites

UnderstandingProposal é a saída futura do adapter, sem campos de aprovação. A
review fica fora dela, vinculada aos hashes de input e proposta. Aprovação exige
respostas às perguntas bloqueantes e resoluções dos conflitos; alvos desconhecidos,
duplicatas e review antiga são inválidos. Rejeição pode preservar pendências.

Review é **metadado declarado**, sem autenticação criptográfica ou autoridade de
execução. A CLI valida consistência, sem comprovar execução de modelo ou identidade
do revisor. O workflow de revisão/aplicação será implementado na AHC-019; não
transformar resultado do modelo em aprovação automaticamente.

Limites iniciais: 128 refs, 16.384 caracteres por valor citado, 128 statements/regras/
perguntas, 16 candidatos, 64 conflitos; refs por item até 32 (conflito tem mínimo 2).
Validar arquivo usa limite padrão 4 MiB, configurável por --max-understanding-bytes.
Manifesto mantém limite próprio do intake. Não truncar citações silenciosamente;
divisão/context budgeting virá com o adapter. Erros dos contratos principais omitem
os valores de entrada; preparação contém os dados do projeto e deve ser tratada
conforme sua privacidade. Não armazenar credenciais ou CoT privado nos registros.

O exemplo é manual/fictício e deixa a review vazia. Os testes comprovam invariantes
estruturais; nenhum fake ou fixture é evidência de entendimento por um modelo real.
