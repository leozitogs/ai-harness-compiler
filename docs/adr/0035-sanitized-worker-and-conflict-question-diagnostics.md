# ADR-0035 — Diagnóstico sanitizado e perguntas de precedência separadas

Status: aceita para implementação offline; eficácia do candidato não estabelecida.

## Contexto

A campanha v4.1 parou na nona invocação com `worker-failed`, exit 2. O código
genérico não permite atribuir causa específica. Entre quatro saídas disponíveis,
o PO confirmou uma regressão: conflito reconhecido e projeto blocked sem pergunta
explícita de precedência. As expectativas e respostas históricas são imutáveis.

## Decisão

O worker emite códigos numéricos fixos 20–38 para etapas e categorias sanitizadas.
Apenas tokens exatos do adapter confiável recebem categorias específicas. Não
persistir mensagens de exceção, stderr, causas encadeadas, prompts ou eventos
intermediários. O adapter histórico, o supervisor, os limites, a contenção e os
contratos TransportReceipt/v1 continuam iguais. `WorkerDiagnostic/v1` deriva uma
categoria da receipt completa; a categoria não certifica causa raiz. Exit 2 e
códigos desconhecidos permanecem unknown. Timeout do supervisor conserva sua
classificação mesmo que o processo termine com outro código.

O candidato explícito `semantic-composition/v4.2` preserva v4.0 e v4.1 byte a byte
nos respectivos prompts e digests. Acrescenta a necessidade de pergunta material
de precedência com fontes de todos os lados de um conflito genuíno. Não inventa
conflitos para normas compatíveis ou titulares simbólicos. Mantém saída v4,
auditoria v5, expectativas, controles de orçamento e defaults anteriores.

`ConflictQuestionDiagnostic/v1` vincula uma análise completa ao seu digest e
recalcula a cobertura: cada conflito deve possuir uma pergunta distinta com
impact=precedence e fontes de todos os lados. Os estados são no-conflicts,
missing-question ou questions-present. O último estado verifica somente vínculos
e tipo; o texto ainda pode estar errado ou irrelevante. Não constitui PASS humano,
não altera assessment, não repara output e não decide disposição do projeto.

Um comando offline inspeciona artefatos explicitamente indicados e grava somente
um arquivo privado novo. Não modifica journals ou resultados originais e não
executa modelo, pesquisa, assets ou código gerado.

## Alternativas e limites

Gravar erro bruto foi rejeitado pelo risco de revelar conteúdo privado. Inferir
quota, login ou schema do antigo exit 2 não tem evidência. Trocar os campos da
receipt v1 ou mudar avaliações históricas prejudicaria hashes e replay. Reparar
automaticamente perguntas ausentes esconderia a saída real e consumiria orçamento.

As cópias de código histórico são evidência de replay, nunca exceção ao gate que
exige source freeze atual para execução nova. Qualquer rodada real precisa de
pedido e autorização próprios. Nenhuma melhoria semântica, resolução de incidente
ou qualificação decorre dos testes sintéticos desta implementação.
