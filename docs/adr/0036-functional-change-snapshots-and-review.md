# ADR-0036 — Mudança funcional vinculada a fontes e aceite separado

Status: aceita para a primeira fatia offline de AHC-031.

## Contexto

O PO autorizou começar a primeira fatia em 18/11/2026. O backlog já exige regra,
exemplos, pergunta material e invalidação de aceite após mudança semântica.
AHC-019/021/022 ainda têm gates mais amplos pendentes; sua conclusão não pode ser
inventada para introduzir um contrato experimental independente de providers.

## Decisão

Acrescentar contratos opt-in `FunctionalChange/v1`, `FunctionalChangeReview/v1`,
`FunctionalReadiness/v1` e `ChangeWorkLog/v1`. A fonte usa UnderstandingRequest/v1,
com input, referências literais e digest já validados. Confirmar uma regra exige
declaração humana vinculada ao digest da regra e do pacote de fontes completo;
trocar a referência mantendo o mesmo ID também invalida a confirmação.

O pacote contém intenção, capacidades selecionadas, regras declaradas/hipotéticas,
exemplos, justificativas de inaplicabilidade, perguntas com dono e impacto,
decisões humanas, requisitos e cenários. Todos os vínculos são locais ao projeto
e validados; perguntas conservam as fontes de todas as regras relacionadas.
Metadata de asset não serve para confirmar comportamento funcional.

Uma pergunta material sem decisão bloqueia prontidão; detalhe de implementação
permanece visível sem criar gate de negócio. Decisões vinculam pergunta e fontes
exatas; não alteram a regra ou a spec automaticamente. Quando a decisão implica
mudar conteúdo, é preciso revisar esse conteúdo e suas confirmações explicitamente.

O digest de mudança cobre todo o conteúdo funcional, fontes e declarações; o
review vincula projeto, ID, revisão e digest. Checklist de cenários preparados
fica em arquivo separado, não afeta o digest nem concede resultado de teste.
Todos os serviços revalidam modelos, inclusive após mutação de objetos aninhados.

Prontidão diferencia blocked, ready-for-human-review, approved e rejected. O
relatório é recalculado na desserialização. Approved significa aceite declarado
do pacote funcional exato; não autentica identidade nem autoriza código, testes,
compilação, instalação ou negócio do projeto alvo. Locators de teste são dados
planejados, sem importação ou execução.

## Alternativas e consequências

Não estender silenciosamente HarnessSpec ou ProjectInput para esta fatia.
Não importar frameworks, criar runtime de agentes ou converter a análise v4.2
em regra confirmada automaticamente. Um grafo global de impacto pertence a
AHC-032; aqui existem apenas referências validadas dentro de uma mudança.

Não introduzir taxonomia fixa de nichos, quotas universais de exemplos ou fluxo
de aprovação por silêncio. Sucesso/falha/fronteira são categorias de cobertura:
inaplicabilidade exige justificativa revisável e cada regra conserva pelo menos
um exemplo concreto. Declaração de dado sintético não certifica privacidade.

Schemas são aditivos. Versões e resultados anteriores mantêm seus bytes e
digests. O congelamento histórico v4.2 conserva o registry antigo em arquivo de
evidência, e o gate de execução atual continua recusando o pedido antigo contra
fontes novas. Nenhum orçamento é reaberto por esse arquivamento.
