# Vínculos estruturais da auditoria — INC-0025

## Problema e implementação

A chamada 10 da rodada v3.4 alterou um caractere de `finding_sha256` em `context-4`.
O JSON era válido no schema anterior, mas o relatório foi corretamente rejeitado
pelo host. A análise recebeu aceite humano independente; a auditoria continua
inválida e não será reescrita ou contada como sucesso.

`component-audit/v4.1` acrescenta uma receita opcional, selecionada explicitamente
por `program_version` em `audit_composition` e `component_audit_schema`. O compilador
projeta no schema, a partir da análise tipada:

- snapshot exato da análise;
- ID, digest e fontes exatas de cada achado;
- identidade e fontes de cada componente, incluindo índice de exceção;
- ID e digest da citação literal de cada fonte.

São constantes estruturais, não decisões semânticas. O modelo continua escolhendo
suporte, materialidade, omissões e explicações. O schema não exige parecer positivo.
As checagens do host permanecem autoritativas: se o provider ignorar o schema,
divergências continuam rejeitadas. Completude, unicidade, consistência entre suporte
global/componentes e vínculos de omissões continuam sendo validados no relatório.

O default é `component-audit/v4.0`, correspondente ao comportamento histórico.
CLI, prompt v4, contrato `SemanticVerifierReport/v4` e seu fingerprint lógico não
mudam. A nova receita não modifica `semantic-composition/v3.4`. A função
`component_audit_program_digest(analysis, version)` identifica separadamente a
receita, incluindo versão, prompt e schema dinâmico. Quem executar a nova receita
deve registrar esse fingerprint junto ao recibo; o fingerprint lógico do relatório
v4 isolado não identifica a estratégia de decodificação ou o ambiente completo.

## Plano e verificação

1. Reproduzir o erro usando somente a resposta final já salva.
2. Acrescentar restrições opcionais, sem alterar a receita histórica.
3. Verificar schemas históricos, rejeição do erro real, julgamentos negativos,
   componentes, exceções e inventários incompletos/duplicados.
4. Revisar as evidências de AHC-021/022 e preservar os gates pendentes.

As regressões confirmam que os oito fingerprints dos schemas de auditoria enviados
na rodada v3.4 continuam idênticos. O retorno inválido é rejeitado pelo schema novo
e pelo host, sem repair ou chamada extra. Respostas históricas válidas são usadas
como fixtures de contrato, não como execução de uma receita nova ou nova avaliação
semântica. Incluem-se análises sem componentes e índices de exceção.

## Limitações e estado do incidente

Nenhuma chamada de modelo foi feita neste incremento. Os dois orçamentos anteriores
continuam consumidos e encerrados. Não há promoção de receita, qualificação de
modelo ou conclusão automática de história.

`const` de arrays e as variantes por identidade são JSON Schema; aceitação,
limites de tamanho e eficácia de decodificação no provider escolhido ainda exigem
verificação de compatibilidade. Não se afirma que o adapter/provedor já exercitou
essa receita. As configurações de ferramentas, isolamento, permissões e budgets
não foram alteradas.

O incidente tem uma correção estrutural candidata verificada offline. Continua
aberto para eficácia operacional: teste de contrato não demonstra que o provider
aceitará o schema ou que deixará de errar. Uma futura execução precisa de protocolo
próprio e autorização concreta; não repetir a chamada 10 ou reaproveitar o orçamento.

Alternativas rejeitadas: aceitar hash aproximado; corrigir o valor devolvido;
repetir silenciosamente a chamada; alterar a receita v4.0 em lugar; exigir supports
no schema. Todas esconderiam erro, alterariam história ou enviesariam a revisão.

Ver [consolidação AHC-021/022](sprint-2-6-prerequisites-review.md).
