# Plano de testes de negócio

Use o relatório `FunctionalReadiness/v1` de uma revisão aprovada. Ele pode
ser emitido pela inspeção funcional com `--review` ou pela consulta de uma
versão específica no arquivo. Consulte o [guia de prontidão](functional-change.md)
e o [guia do arquivo](functional-change-archive.md).

```sh
uv run python scripts/plan_functional_tests.py --readiness .factory/readiness.json export --plan .factory/business-test-plan.json
uv run python scripts/plan_functional_tests.py --readiness .factory/readiness.json verify --plan .factory/business-test-plan.json
```

O plano liga cada cenário a um requisito e a um exemplo com estado inicial,
ação e resultado esperado. Os catálogos também trazem regras, fontes por
pointer, perguntas, respostas e justificativas de cobertura inaplicável.
O relatório de prontidão preserva o conteúdo integral das fontes e da
revisão. Mantenha os dois arquivos sob os controles de acesso do projeto.

A exportação exige um destino novo e valida entradas e saída de até 8 MiB
cada. Preserve os bytes gerados em UTF-8, pois `verify` compara com a mesma
projeção determinística da revisão aprovada. Caso a gravação seja
interrompida, confira com `verify` antes de usar o arquivo. Uma revisão
histórica pode gerar seu próprio plano, com número e digest próprios.
Mudanças de comportamento exigem nova revisão antes de exportar outro plano.

Os locators conservam o estado `not-run`, inclusive quando o arquivo de
teste ainda não existe. A validação desta fatia usa exemplos sintéticos.
A execução de testes de negócio e a avaliação com projetos reais continuam
na esteira de AHC-031.
