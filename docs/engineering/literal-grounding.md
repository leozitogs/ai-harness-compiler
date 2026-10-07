# AHC-022 — Extração literal e verificação de citações

Este primeiro incremento prepara evidências antes da análise e verifica propostas
salvas. Não transforma todos os critérios em regras automaticamente e não qualifica
modelos. Ver ADR-0013.

```sh
factory prepare-grounding examples/project-definition
factory verify-grounding docs/evidence/model-study-20261007/qwen3-understanding.json \
  --output output/new-quotation-report.json
factory schema grounding-extraction
factory schema grounding-quotation-report
```

prepare-grounding imprime JSON; verify-grounding exige arquivo novo. Retorno zero
indica relatório estrutural válido, inclusive com zero citações encontradas.
O input salvo é limitado a 2 MiB. A validação dos contratos recompõe os inventários
e cruza as propostas com o snapshot, sem rede, ferramentas ou leitura de assets.

## O que cada dado significa

| Dado | Significado | Limite |
|---|---|---|
| atoms | Valores literais e suas origens no manifesto | São dados não confiáveis |
| acceptance-criterion | Localização estrutural de um critério | Pode ser requisito técnico ou produto; não necessariamente regra |
| asset-metadata | Path e description fornecidos | Nenhum conteúdo foi aberto |
| excluded_references | Afirmações externas/perfil fornecido preservados fora da extração | Nenhum aceite externo é criado |
| quoted_by_rules | IDs de regras extraídas que repetem a citação e usam a fonte | Condição, resultado e suporte semântico não foram julgados |
| semantic_status | not-established | Necessita revisão semântica separada |

Campos, IDs, ordem, quotes, pointers e exclusões são determinísticos e completos.
O limite de 512 átomos rejeita excessos em vez de descartar dados silenciosamente.
Modificar estruturas aninhadas em memória requer revalidar o documento antes
de utilizá-lo; as funções públicas fazem essa revalidação.

## Reprodução do problema

Os relatórios em docs/evidence/ahc-022-literal-baseline verificam, offline, as duas
propostas já publicadas no estudo inicial, sem novas chamadas ou tuning:
Qwen3 Instruct e Qwen3.5 têm zero critérios citados por BusinessRule extraída.
São quatro critérios de aceitação no input de cada piloto. O resultado reafirma
a lacuna estrutural observada; não mede a qualidade de um novo prompt.

Próximo incremento: análise baseada nos átomos, verificação de suporte e repair
limitado, com identidade/versionamento do prompt e comparação no development.
A revisão da rubrica/expectativas permanece pendente. Holdout não foi executado.
