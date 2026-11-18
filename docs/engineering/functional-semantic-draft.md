# Preparar uma mudança funcional a partir de análise revisada

Use o comando abaixo com um `SemanticAssessment/v4` completo, já revisado
e com resultado `pass`. Forneça o SHA-256 canônico do assessment completo
registrado na revisão. Use `canonical_project_digest(assessment.model_dump())`
após validar o JSON com `SemanticAssessmentV4`. O digest abrange caso,
rubrica, análise, declaração humana e resultado.

```sh
uv run python scripts/draft_functional_change.py --assessment .factory/assessment.json --expected-assessment SHA256_DO_ASSESSMENT --change-id review-display --intent "Clarificar as condições de exibição" --capability store-record --rule criterion-1 --question issue-1 product-owner criterion-1 --output .factory/change-draft.json
```

A intenção é declarada pelo operador. Repita `--capability` e `--rule` para
delimitar o escopo. Para cada pergunta da análise, passe `--question`
com o ID, o responsável e um ou mais IDs de regras selecionadas. As
referências da pergunta precisam cobrir as regras vinculadas. O comando
recusa a projeção quando um conflito carece de pergunta de precedência
com as fontes dos dois lados ou quando um átomo necessário foi rejeitado.
Um projeto com disposição `safely-rejected` fica fora da projeção.

O arquivo criado é um `FunctionalChange/v1` com hipóteses e perguntas.
O recibo na saída padrão contém os digests do assessment e da mudança.
Guarde o recibo, o assessment e os parâmetros usados. Revise as hipóteses,
as demais normas do assessment, os exemplos e os requisitos antes do aceite
funcional. Este passo prepara o rascunho, que pode ser consultado e
arquivado com os comandos existentes. [Guia do arquivo](functional-change-archive.md)

Os caminhos ficam dentro da raiz informada e o comando cria um arquivo
novo. Assessment e rascunho têm limite individual de 1 MiB. A saída inclui
o manifesto original e deve receber o mesmo tratamento de privacidade
das suas fontes. A demonstração automatizada usa dados sintéticos e liga
a projeção ao arquivo local, preservando a pergunta material em aberto.
