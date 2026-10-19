# ADR-0022 — Revisão humana preserva proveniência por componente

Status: aceito para implementação em 2026-10-19; AHC-021/022.

## Decisão

Adicionar `SemanticHumanReview/v3`, `SemanticAssessment/v3` e comando offline
`assess-analysis-v3`, consumindo análise v3 sem conversão para v2. Reutilizar caso
AssessmentCase/v2 e rubrica v2: suas expectativas não mudam de significado.

Além do parecer por achado, a revisão registra nome/índice/fontes de cada componente.
Pass em suporte exige inventários completos e positivos. Componente negativo não
pode coexistir com suporte positivo ao achado inteiro. Alterar texto, fonte, posição
ou aplicabilidade de guard invalida o snapshot de análise e o hash do achado.

Sem revisão humana, aprovação de expectativas e rubrica, a avaliação nunca passa.
Falhas objetivas continuam fail mesmo sem julgamento completo. Parecer de modelo não
é importado como revisão humana; declarações são humanas declaradas, não autenticadas.
Nenhum resultado autoriza compilar ou estabelece qualificação por si só.

## Compatibilidade e limites

V2 permanece disponível e inalterada. Casos e rubrica podem ser compartilhados por
versões, mas outputs e revisões não são migrados automaticamente. O código de
assessment é versionado separadamente para preservar hashes/semântica histórica.
Os testes usam declarações sintéticas e não aprovam respostas reais.

Guards têm aplicabilidade no hash por achado e no snapshot integral; a revisão de
suporte considera a restrição completa, não somente suas duas frases. A correção
semântica continua sendo responsabilidade do revisor. Inventários não a demonstram.
