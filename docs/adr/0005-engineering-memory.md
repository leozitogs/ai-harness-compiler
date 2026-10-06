# ADR-0005 — Memória de engenharia por revisões e recuperação

Status: implementado nesta proposta; registro DE-0001 aguarda revisão explícita.

## Contexto

O PO solicitou documentação permanente que registre estado, decisões, desafios,
erros e soluções e ajude colaboradores de código e agentes a aprender com experiências.

## Decisão

Usar contratos tipados DE/DOC/ADR/INC/LES/RUN/EXP, revisões JSON append-only em Git
e índice SQLite FTS5 reconstruível. Integrar consulta nos especialistas e nas
instruções do repositório. Separar drafts, fatos verificados e decisões revisadas.
Preservar contexto de aplicação, limitações, tentativas e evidências de cada solução.

## Consequências

Memória é portátil entre clones e revisável por diff. Captura de falhas não inventa
diagnóstico ou promoção. Hashes verificam a versão da evidência, não sua verdade.
Recuperação padrão exclui conteúdo desatualizado, drafts e registros substituídos.
Aprendizado ocorre pelo uso de experiências recuperadas; treino de modelos exige
um experimento separado, dataset adequado e avaliação de regressão.

O sistema local não fornece identidade autenticada, assinatura, sincronização
distribuída ou indexação incremental de grande escala. Foram escolhidos limites
explícitos para a necessidade atual, com evolução posterior orientada por medição.
