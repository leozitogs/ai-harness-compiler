# Correções dos achados da revisão independente

Reproduzidas em 2026-10-06 antes da alteração, usando o script fornecido pelo PO.
Ambas as contradições eram aceitas; o bundle de F1 compilava e passava integridade.

## F1 — Preservação do snapshot fornecido

ProjectDNA agora exige cobertura exata dos IDs canônicos e fornecidos, além de
igualdade por ID das fontes e afirmações com ProjectInput.evidence_pack. Edição,
remoção, adição desvinculada e reativação de fonte rejeitada são bloqueadas. Ordem
das listas pode mudar sem alterar o significado. Revisões legítimas devem atualizar
o input e regenerar sua proveniência consistentemente.

## F2 — Consistência interna do relatório

BenchmarkCase exige duas ou mais amostras, hashes iguais, tamanhos/contagens iguais
e mediana calculada a partir das durações. BenchmarkReport exige IDs de casos únicos
e quantidade de amostras igual a runs_per_fixture em cada caso. Mediana é armazenada
sem arredondamento; tabelas de apresentação podem arredondar sem alterar o JSON bruto.

## Verificação e compatibilidade

207 testes passaram em Windows/Python 3.13.7, todos os extras, sem skips:

```sh
pytest -q -p no:cacheprovider --basetemp .factory/review-fixes-full-1
```

Os 17 novos casos em tests/test_review_regressions.py exercitam as reproduções,
alterações/remoções/reativação, referências extras, reordenação válida, hashes,
mediana, contagem, tamanhos e unicidade. Erros de IR são rejeitados antes da emissão;
relatórios contraditórios falham tanto em validação de objetos quanto JSON.

A baseline publicada continua válida e não foi alterada. Seu digest de código
identifica a execução anterior, não o código corrigido. São correções de invariantes
dos contratos existentes, sem novo formato de IR. Snapshots consistentes continuam
aceitos; não há autenticação externa, prova de verdade ou novo SLO.
