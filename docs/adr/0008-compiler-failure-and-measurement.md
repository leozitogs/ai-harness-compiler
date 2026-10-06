# ADR-0008 — Falha explícita e medições offline

Estado: adotada na AHC-004; incremento sujeito a revisão por PR.

## Contexto

O compilador já recusava saída existente, mas propagava mensagens específicas do
filesystem e emitia o manifesto antes de terminar outros arquivos. Faltavam fixtures
de três domínios e medições reais. Critérios: AHC-004 no backlog canônico.

## Decisão

Reservar exclusivamente a saída nova, emitir manifesto por último e distinguir
falhas de reserva/escrita. Preservar saída parcial com diagnóstico e recusar reuso;
não apagar arquivos automaticamente. Benchmark offline verifica três fixtures,
integridade e reprodução em builds repetidos; registra amostras/ambiente/hashes,
sem SLO ou claims de eval do produto.

## Alternativas e limites

Rollback recursivo exigiria garantias de propriedade/concorrência antes de remover
arquivos. Rename sobre destino tem diferenças entre plataformas e pode sobrescrever
diretórios vazios. Não adotamos essas alternativas nesta história. Publicação
transacional/instalação exige contrato futuro próprio (AHC-012).

Manifesto por último melhora diagnóstico, sem prometer atomicidade ou tolerância
a falta de energia. Benchmark é medida local pequena, não comparação de providers,
simulação de agentes ou prova de capacidade operacional.
