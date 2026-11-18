# Uma regra, três exemplos e uma pergunta material

`change.json` é uma fixture **inteiramente sintética**, de domínio não declarado,
com uma regra de conclusão de lote, três exemplos e vínculos de cenário/requisito.
O campo de confirmação usa `synthetic-reviewer`: demonstra o contrato e não
registra aceite real do PO. A pergunta sobre o tratamento de excesso permanece
aberta, com responsável `product-owner` e impacto `outcome`.

Na raiz do repositório, com `.factory/` já existente:

```sh
uv run python scripts/inspect_functional_change.py --input examples/functional-change/change.json --output .factory/functional-demo-readiness.json
```

O resultado esperado é `blocked`, com `unresolved-question: overflow-question`.
Escolher um nome novo de saída a cada execução: o comando recusa sobrescrita.
Ele não resolve a pergunta, testa o produto, executa os locators de teste ou
compila o harness. `execution_status` e `test_execution_status` continuam not-run.

Os locators apontam ao teste de cobertura dos exemplos no próprio compilador.
São verificações dos contratos desta fatia, não uma suíte de negócio para um
produto gerado. Para adoção real, fornecer fontes e declarações humanas reais,
revisar exemplos/requisitos e implementar a verificação de negócio no projeto
alvo; não reutilizar as declarações sintéticas da fixture como aceite.
