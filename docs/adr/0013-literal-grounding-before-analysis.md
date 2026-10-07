# ADR-0013 — Evidência literal antes da análise

Status: aceito para implementação estrutural; aceite semântico do PO pendente.

## Contexto

Os pilotos preservados de Qwen3 e Qwen3.5 produziram zero BusinessRule, mesmo
com critérios explícitos no backlog. INC-0007 registra também conflitos indevidos
e interpretações não sustentadas. Um JSON válido não demonstra compreensão.

## Decisão

Introduzir GroundingExtraction/v1: snapshot e inventário completos, átomos literais
com ponteiro, citação exata, referência original, categoria estrutural e trust.
A transformação é pura e independente de provider. Nenhum texto é executado.

Concepção, branding, restrições, descrições, critérios e domínio declarado são
preservados. Assets fornecem apenas path/description; seu conteúdo não foi lido.
Perfis fornecidos e afirmações externas permanecem no snapshot e em referências
explicitamente excluídas da extração, sem reclassificação ou promoção. Isso inclui
afirmações de fontes rejeitadas: não podem reaparecer como fatos extraídos.

GroundingQuotationReport/v1 vincula extração e proposta ao mesmo snapshot e
registra, para cada critério, quais BusinessRule com origin=extracted repetem
a citação exata e referenciam sua fonte. O validador recompõe esse resultado,
rejeitando omissões e associações contraditórias.

Citação não prova condition/outcome, causalidade, conflito ou regra de negócio.
O relatório mantém semantic_status e model_qualification em not-established.
Não muda notas dos evals, rubrica congelada, revisão ou estado do backlog.

## Alternativas e consequências

- Extrair regras automaticamente por regex confundiria texto e significado.
- Apenas pedir ao modelo que cite o input não controla perda de critérios.
- A extração explícita permite futura análise com evidências separadas, mas aumenta
  o volume de contexto. Até 512 átomos, 128 referências e 16 KiB por citação;
  excesso é rejeitado, sem truncamento silencioso.
- Estes contratos são aditivos. UnderstandingRequest/Proposal e a IR mantêm suas
  versões. O estudo Ollama atual ainda não consome automaticamente os átomos.
- A análise/repair versionados e comparações de desenvolvimento serão outro
  incremento, depois da revisão da rubrica/expectativas prevista na Sprint 2.5.
