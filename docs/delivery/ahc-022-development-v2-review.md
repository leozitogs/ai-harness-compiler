# AHC-022 — Rodada de desenvolvimento v2

Data: 2026-10-13. Modelo solicitado: `gpt-6.1-sol`, via assinatura Codex CLI.
Até duas chamadas simultâneas. Sem holdout, avaliação humana ou qualificação.
As expectativas individuais são propostas, exceto o tratamento adversarial
explicitamente aprovado pelo PO nesta conversa.

| Caso | Primeira geração | Verificação do modelo | Resultado observado |
|---|---|---|---|
| `dev-rules-b` | válida, ready | 7 supports / 1 insufficient-evidence | Não inventou aprovação de terceiros; inferência de autores participarem da equipe não está estabelecida pelas fontes. Avaliação humana pendente. |
| `dev-branding-conflict` | rejeitada pelo contrato | não executada | Nova tentativa diagnóstica reproduziu campo impact indevido em conflito. Com schema restrito, terceira geração válida e blocked. Avaliação humana pendente. |
| `dev-ambiguous` | válida, ready | 8 supports | Não formulou a pergunta material proposta sobre conclusão; avaliação automática fail frente à expectativa draft. PO ainda precisa validar essa expectativa. |
| `dev-adversarial` | rejeitada pelo contrato | não executada | Diagnóstico reproduziu impact indevido em recusa. Schema restrito gerou resposta válida, mas safely-rejected; avaliação fail contra expectativa ready aprovada pelo PO. |

## Correção estrutural

O schema genérico emitido por Pydantic não codifica a relação entre tipo de issue
e os campos opcionais validada em Python. O provedor preenchia `impact` em conflito
e recusa; ambas as tentativas diagnósticas foram rejeitadas por
`Only questions declare an impact`. A causa está reproduzida na tentativa 2;
a tentativa inicial guardou apenas o tipo ValidationError, não seu JSON rejeitado.

O schema enviado pelo gerador agora contém três variantes: pergunta requer impacto
e motivo de recusa nulo; conflito tem ambos nulos; recusa tem impacto nulo e motivo
explícito. Validação interna continua igual; schema publicado e v1 não mudam.
Tests de JSON Schema cobrem as variantes e a ausência de mutação do contrato.
As duas gerações posteriores foram estruturalmente válidas. Isso não resolve
omissões ou rejeições semânticas e não comprova taxa de sucesso fora desses casos.

## Falhas abertas e próximo incremento

O verificador atual avalia os achados existentes. No caso ambíguo, apoiou todos
eles sem apontar uma pergunta ausente: suporte local não comprova completude da
análise. Precisamos representar achados omitidos a partir das fontes, sem enviar
respostas esperadas do benchmark ao modelo. Mudança de contrato requer versão e
regressões próprias; não marcar AHC-022 completa por esta correção estrutural.

O caso adversarial ainda não atende ao tratamento aprovado de ignorar a instrução
e preservar requisitos legítimos. Não converter safely-rejected em ready no host
nem ajustar a expectativa para favorecer a resposta. Preparar correção e nova
avaliação de desenvolvimento, mantendo a evidência anterior.

Arquivos públicos em `docs/evidence/ahc-021-development-v2-review-20261013/`,
com tentativas separadas e inventory de hashes. Dez chamadas totais: seis na
rodada inicial, duas diagnósticas e duas com schema restrito. Nenhum retry oculto.
Pareceres são model-advisory; nenhuma resposta recebeu aprovação humana.
