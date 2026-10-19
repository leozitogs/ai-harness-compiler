# Sprint 2.5 — Review e fechamento de foco

Data: 2026-10-19. PO solicitou concluir tarefas e finalizar a sprint. O foco é
encerrado com resultado parcial e trabalho remanescente explícito. Não houve
cerimônia síncrona, aceite humano das respostas ou conclusão das histórias AHC-021/022/023.
O Sprint Goal de qualificação não foi alcançado; nenhum perfil está qualificado.

## Incremento entregue

- Corpus e rubrica versionados; os oito comportamentos de desenvolvimento agora
  têm aprovação explícita do PO. Manifesto congela bytes de casos e rubrica.
- Extração literal, distinção entre declarações e hipóteses, perguntas materiais,
  inventário de fontes, omissões e proveniência por componente.
- Análise v3 com guards separados; auditoria consultiva v4 e novo assessment/revisão
  humana v3 preservam fontes, exceções e aplicabilidade. Não autorizam compilação.
- `assess-analysis-v3` funciona offline; sem revisão real retorna not-run ou falha
  objetiva, nunca pass. Contratos antigos e resultados históricos preservados.
- Modelo principal operacional e alternativa local explícitos; falhas não acionam
  fallback. Atualizações de dependências integradas no PR #39 e antecedentes.

## Rodada final de desenvolvimento

Modelo solicitado `gpt-6.1-sol` via Codex CLI, identidade observada não autenticada.
Oito casos, sete análises válidas e uma rejeitada estruturalmente. As sete análises
válidas tiveram a disposição esperada. Isso não constitui sete aprovações semânticas.
Foram quinze chamadas na rodada inicial e duas na recuperação, máximo duas simultâneas,
timeout 180 s/chamada, sem tools, sem retry oculto e sem holdout.

| Caso | Geração/disposição inicial | Diagnóstico consultivo |
|---|---|---|
| dev-adversarial | válida / ready | uma possível omissão |
| dev-ambiguous | válida / blocked | um componente sem suporte suficiente |
| dev-branding-conflict | válida / blocked | uma possível omissão |
| dev-compatible-rules | inválida | componentes de regra em requisito; auditoria não executada |
| dev-new-domain | válida / ready | sem componente negativo ou omissão reportados |
| dev-rules-a | válida / ready | duas possíveis omissões |
| dev-rules-b | válida / ready | uma possível omissão |
| dev-unread-assets | válida / ready | sem componente negativo ou omissão reportados |

O schema enviado ao provedor agora separa variantes business-rule, requirement e
needs-clarification. Programa `semantic-composition/v3.1`: contratos persistidos não
mudam; schema de geração é restringido e testado. Nova tentativa de regras compatíveis
foi válida/ready com dois guards e uma possível omissão. A falha original permanece.
Não houve rodada completa do v3.1 nem comparação estatística controlada de qualidade.

O auditor usa o mesmo modelo e pode apontar falsos positivos. Seus diagnósticos são
insumos para revisão, não conclusões humanas. Oito assessments offline dos outputs
válidos (incluindo recuperação) ficam sem revisão humana; os estados estão nos arquivos.
[Inventário e hashes](../evidence/sprint-2-5-final-20261019/inventory.json).

## Decisão de qualificação e trabalho remanescente

Nenhuma promoção: falha estrutural na rodada inicial, revisão semântica ausente e
diagnósticos não adjudicados. O v3.1 não foi avaliado em toda a matriz. O modelo local
não foi reavaliado nesta rodada; seus ensaios anteriores não são convertidos para v3.
Isto é ausência de qualificação, não prova de inferioridade geral dos modelos.

Holdout preservado: pré-condições ainda não satisfeitas. A revisão humana deve julgar
fontes/componentes, cobertura e diagnósticos, incluindo falsos conflitos e bloqueios.
Depois, corrigir se necessário, congelar candidato, preparar expectativas reservadas
revisáveis sem tuning no holdout e executar a matriz de qualificação com repetições,
telemetria, cold/warm e orçamento. AHC-020 continua dependente desse resultado.

| História | Estado no fechamento | Remanescente |
|---|---|---|
| AHC-021 | parcial, não Done | revisão dos outputs e protocolo reservado atualizado |
| AHC-022 | parcial, não Done | adjudicar diagnósticos e comparar candidato completo com baseline |
| AHC-023 | parcial, não Done | matriz de qualificação e decisão baseada em avaliação reservada |

As issues permanecem abertas. A Sprint 2.6 está na esteira com AHC-024/025/026 e gates
de entrada, não iniciada. O remanescente 021/022/023 tem precedência sobre promoção,
experimentos reservados e treinamento. Não se declarou pré-requisito concluído para
forçar um TaskGraph executável da sprint futura.

## Retrospectiva técnica proposta

Melhoria: expressar no schema do provedor as invariantes entre tipo e campos antes
de chamadas caras. Regressão agora cobre os três tipos. Manter verificação interna
independente, preservar cada tentativa e separar correção estrutural de sucesso semântico.
Esta nota não declara uma reunião de retrospectiva realizada.

## Verificação de engenharia

764 testes passaram, sem skips, com todos os extras. Incluem revisão parcial,
componente negativo, fontes/índices trocados, guard stale, hash alterado, estado
forjado e CLI offline que recusa sobrescrever saída. Lint, formatação, mypy,
schemas e planos regenerados são verificados; integração segue CI e PR.
