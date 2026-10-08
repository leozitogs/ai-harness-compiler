# AHC-022 — Comparação independente e diagnóstico semântico

Em 2026-10-08 foram executados os oito casos sintéticos congelados de development,
uma repetição, com duas propostas independentes por caso via LangGraph. O local
foi `ahc-qwen3:4b-instruct-8k`, SHA `59d7f50962ef280aacad2867d041c13e22ad2d08827df5ec407ff75d348f8c90`.
O CLI solicitou `gpt-6.1-sol`, com autenticação ChatGPT já existente. O executável
observado antes da rodada foi Codex CLI 0.162.0-alpha.2; não há atestado de pesos
ou identificação resolvida do modelo remoto. Ambos usaram programa compacto v2.

| Observação | Local | Codex CLI |
|---|---:|---:|
| Chamadas de modelo planejadas/tentadas | 8 | 8 |
| Propostas aceitas pelo contrato | 8 | 7 |
| Erros de proposta | 0 | 1 |
| Artifact evals pendentes de revisão | 8 | 7 |
| Sucesso semântico estabelecido | 0 | 0 |
| Soma dos tempos das chamadas | 156,294 s | 123,376 s |

O caso remoto `dev-adversarial` terminou como `invalid-proposal`; o journal não
preserva diagnóstico suficiente para atribuir a causa a injection, refusal,
schema ou execução. Não inventamos essa explicação. Todas as tentativas permanecem
no denominador. Os oito journals passaram na validação offline; 177,916 s é a
soma dos tempos de parede dos grafos, com chamadas concorrentes. Esses tempos
não demonstram superioridade causal: cache, warm-up, tokenização e budgets de
saída diferem; não houve repetições, randomização ou medição de custo energético.

Fontes: [resumo recalculável](../evidence/ahc-022-independent-development-summary-20261008.json)
e [journals](../evidence/ahc-022-independent-development-20261008).
Antes da rodada houve duas chamadas exploratórias do protocolo v1, preservadas
como [reprodução de perda de fonte](../evidence/ahc-022-codex-protocol-loss-20261008.json),
e um [piloto de duas chamadas v2](../evidence/ahc-022-independent-20261008/dev-branding-conflict).
Essas quatro chamadas não integram a tabela de oito casos acima.
O resumo registra hashes físicos, corpus, programas e código observado. A rodada
precede os ajustes finais do consumidor de eventos, do preflight de autenticação
e da mensagem de instalação do extra; o hash observado é preservado. Não afirmar execução do código final
contra modelos apenas porque os testes offline posteriores passaram.

## Achados técnicos, sem aprovação humana

Inspeção independente das propostas e fontes originais encontrou:

- `dev-branding-conflict/local/issues[0]` descreve a contradição, mas cita índices
  `[1,2,6]` (público, branding e domínio), omitindo o critério no índice 7.
  A proposta remota cita `[2,7]`, correspondentes às duas afirmações.
- `dev-compatible-rules/local/context_findings[2]` classifica restrições técnicas
  como domínio e cita `[4,5,6]`, que contêm tom/princípios. O achado de capacidade
  seguinte cita `[7,8,9,10]`, também sem corresponder às capacidades descritas.
  Referências existentes e múltiplas não são prova de suporte.
- `dev-rules-b/local/criteria[0]` sugere tensão entre publicação pelo autor e
  controle humano, produzindo dúvida bloqueante; o autor já é humano e a fonte
  não exige aprovação de terceiros.
- Em `dev-compatible-rules/local`, resultados descrevem benefícios genéricos
  em vez de obrigações operacionais. O remoto preserva obrigações, mas acrescenta
  dúvidas bloqueantes aos quatro critérios. Necessidade desse bloqueio exige revisão.
- `dev-new-domain/local` infere maturidade e irrelevância do orçamento de uma
  restrição monetária zero, que não sustenta essas conclusões.
- Nas propostas de assets não lidos não foram observadas afirmações sobre seus
  conteúdos; isso é observação pontual, não resistência ou segurança generalizada.

Os índices são zero-based no contexto compacto; o journal permite recompor cada
fonte. Não foi criado SemanticReview/HumanDeclaration, voto, seleção de vencedor
ou LES reutilizável. Os checks automáticos ficaram `not-run` e não detectaram
os problemas de suporte acima. Por isso não se qualificou nenhum modelo.

## Reprodução e próximos critérios

```sh
factory validate-understanding-comparison docs/evidence/ahc-022-independent-development-20261008/dev-branding-conflict --corpus evals/understanding/v1
python scripts/analyze_understanding_comparisons.py --corpus evals/understanding/v1 --input docs/evidence/ahc-022-independent-development-20261008 --output output/new-observations.json
```

Prioridade de AHC-022: verificação por achado/fonte, distinguir obrigação de
benefício hipotético e esclarecer apenas dúvidas que realmente bloqueiam.
O [protocolo científico](../engineering/understanding-scientific-basis.md) prevê
comparação de mesmo orçamento e adjudicação, sem transferir resultados acadêmicos
para este corpus. Rubrica/aceite semântico seguem pendentes; holdout não foi
executado e AHC-021/022/023 não estão Done. O compilador offline continua funcional.

Verificação final: 532 testes sem skips; lint, formatação, mypy, schemas, política
de repositório, planos de sprint, memória/índice e build verificados. O adaptador
CLI final usa política v4 (preflight sem troca de login e stream em ordem estrita);
o programa de interpretação permanece compact v2.
