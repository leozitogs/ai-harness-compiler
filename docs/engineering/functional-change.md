# Mudanças funcionais — primeira fatia offline

AHC-031 introduz contratos e inspeção executável antes de plano técnico ou agentes.
A [fixture sintética](../../examples/functional-change/README.md) demonstra uma
regra, três exemplos, pergunta material, requisito e locators de teste.

## Artefatos e fontes

| Artefato | Responsabilidade | Não concede |
|---|---|---|
| FunctionalChange/v1 | Conteúdo funcional, fontes, regra, exemplos, perguntas, requisitos e cenários | Correção semântica ou execução |
| RuleConfirmationV1 | Confirmação declarada de regra e fontes exatas | Aprovação do pacote inteiro |
| QuestionDecisionV1 | Resposta humana vinculada à pergunta e suas fontes | Reescrita automática das regras |
| FunctionalChangeReview/v1 | Aprovar/rejeitar projeto/ID/revisão/digest exatos | Autenticação ou autorização de compilação |
| ChangeWorkLog/v1 | Cenários preparados, fora do conteúdo funcional | Testes executados ou aprovados |
| FunctionalReadiness/v1 | Estado e bloqueios recalculados | Qualificação do modelo ou aceite de história |

Reusar UnderstandingRequest/v1 preserva o contrato de fonte literal. Validar e
normalizar o ProjectInput antes de calcular seu digest; não derivar hashes de
defaults ainda não normalizados. A confirmação de regra e a decisão usam
`source_sha256` do **pacote completo**: uma substituição de pointer ou valor com
o mesmo ID precisa de nova declaração, mesmo dentro do mesmo projeto.

Regras, exemplos, perguntas, requisitos e cenários têm IDs globais únicos dentro
da mudança. Cada cenário liga um exemplo a um requisito que contém sua regra.
O locator tem formato `tests/test_file.py::test_function` ou subpastas de tests,
sem paths absolutos, travessia de diretórios, argumentos ou comandos. O contrato
não comprova existência, descoberta por pytest ou qualidade desse teste.

## Prontidão e revisão

- Regra sem confirmação permanece bloqueada, inclusive quando marcada como hipótese.
- Cada regra precisa de cobertura de sucesso, falha e fronteira, ou justificativa
  explícita para categoria inaplicável; ao menos um exemplo concreto é obrigatório.
- Regra sem requisito, requisito sem cenário e exemplo sem cenário geram bloqueios próprios.
- Pergunta com impacto rule, authorization, outcome ou precedence exige decisão
  declarada vinculada ao snapshot. Implementation-detail não bloqueia por si só.
- Sem bloqueios, o estado é ready-for-human-review. Approved/rejected exigem review
  exato; revisão stale é preservada como bloqueio, nunca reaproveitada como aceite.

Alterar exemplo, fontes, regra, requisito, decisão, intenção, capacidades ou revisão
muda o digest e exige revisão nova. Se uma regra/pergunta mudou, suas declarações
antigas tornam o pacote inválido e devem ser retiradas ou substituídas de forma
explícita numa revisão nova. O CLI nunca faz essa retirada pelo usuário.
Marcar um cenário como preparado no worklog não muda a spec nem o review e não
declara resultado de teste. Validação e registro não substituem julgamento humano.

## Operação

```sh
uv run python scripts/inspect_functional_change.py --input examples/functional-change/change.json --output .factory/readiness-new.json
```

`--review arquivo.json` é opcional e só lê a declaração fornecida. Os caminhos
devem ficar na raiz de repositório indicada por `--repository`; inputs têm limite
de 1 MiB e reports de 2 MiB. A pasta de saída precisa existir. O comando grava um
arquivo novo e recusa sobrescrita; uma falha de I/O pode deixar um arquivo parcial,
que não deve ser reutilizado como evidência. Erros não imprimem o input privado.

Exit 0 significa que um relatório válido foi emitido, inclusive com status blocked
ou rejected. Verificar seu status, bloqueios e snapshot; exit 0 não significa PASS
de negócio. O comando não lê assets, chama providers, importa locators, executa
código gerado, altera input ou instala resultado. O build padrão não usa o contrato.

## Limites da fatia

A classificação de regra e o conteúdo dos exemplos/perguntas ainda exigem revisão
semântica. HumanDeclaration registra declaração, não identidade autenticada.
Confirmar uma regra não prova que as fontes são verdadeiras, e justificar uma
exceção de cobertura não prova inaplicabilidade. O review deve avaliar esses pontos.

Archive, comparação entre revisões, política de retenção, importação de respostas
de entendimento, exportação de suíte de negócio e o grafo global de impacto ficam
para incrementos posteriores. Esta entrega não encerra AHC-031, AHC-019/021/022
ou a Sprint 2.6.
