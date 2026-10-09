# Entendimento e verificação semântica v2

Geração, diagnóstico do modelo e avaliação humana usam contratos distintos.
Fontes são átomos literais do input; assets continuam sem leitura e claims externos
excluídos não voltam a ser fontes aceitas. V1 e resultados históricos ficam intactos.

## Operação

As duas primeiras chamadas são opt-in e consomem o modelo por Codex CLI com login
ChatGPT. Avaliação de arquivos salvos é offline. Diretórios de saída precisam
existir; arquivos existentes nunca são sobrescritos.

```sh
factory analyze-project-v2 ./project-definition --output ./analysis-v2.json
factory verify-analysis-v2 ./analysis-v2.json --output ./advice-v2.json
factory assess-analysis-v2 ./analysis-v2.json --case ./case-v2.json --rubric ./evals/understanding/v2/rubric.json --output ./assessment-v2.json
```

`--review ./human-review-v2.json` recebe apenas parecer humano real. Sem parecer,
expectativas do caso aprovadas e rubrica aprovada, não existe `pass`. Avaliação
retorna 0 apenas para `pass`, 1 para `fail`/`not-run`. Retorno 0 de geração/verificação
significa arquivo estruturalmente válido salvo, nunca aprovação semântica. Erros
técnicos não geram relatório de rejeição segura.

Schemas `semantic-*-v2.schema.json` descrevem os contratos. `AssessmentCase/v2`
contém projeto, comportamento esperado e obrigações com pointer/quote literal e
disposição `rule`, `required-question` ou `requirement`. Conflitos obrigatórios e
recusas possuem pointers específicos. Casos prontos exigem obrigações positivas;
casos bloqueados exigem pergunta material ou conflito. Expectativas individuais
ainda serão apresentadas ao PO antes do congelamento do corpus v2.

O verificador relata `supports`, `contradicts` ou `insufficient-evidence` e avalia
materialidade. Ele não preenche `SemanticHumanReview/v2`. Alteração de condição,
exceção, fonte, classificação ou motivo de recusa exige novo parecer. Nenhum
comando desta entrega autoriza compilação ou qualifica o modelo.

## Próximos gates

1. Validar com o PO expectativas observáveis dos casos de desenvolvimento v2.
2. Revisar respostas e diagnósticos, corrigindo falsos positivos e falsos bloqueios.
3. Congelar corpus, programa e candidato antes do holdout reservado.
4. Qualificar entendimento nos seis critérios antes do blueprint e da autorização
   própria de compilação.

O verificador é uma segunda chamada, não um modelo cientificamente independente.
Concordância não demonstra verdade. Testes de contrato e smokes de execução não
medem precisão ou desempenho em produção. Credenciais e reasoning privado não são
persistidos; pareceres contêm explicações breves com evidência.

`program_sha256` é fingerprint lógico validado do prompt/schema genérico do
verificador, não identidade completa da execução: dimensões dinâmicas e política
do adaptador são verificadas por contratos/código próprios. `requested_model` é
modelo solicitado, não identidade observada/autenticada. A CLI v2 salva apenas o
artefato final; falhas não têm journal de tentativa e não equivalem ao runner de
sessões supervisionadas v1. Este incremento não mede latência reproduzível.
