# Regras, guards e proveniência por componente

```sh
factory analyze-project-v3 ./project-definition --output ./analysis-v3.json
factory verify-analysis-v4 ./analysis-v3.json --output ./advice-v4.json
```

Chamadas explicitamente dependentes do modelo principal Codex CLI, sem fallback.
Arquivos existentes não são sobrescritos. Sucesso do comando significa artefato
válido salvo, não sucesso semântico, autorização de compilar ou qualificação.

`EvidenceText` contém interpretação e `source_atom_ids`. Condição, resultado e cada
exceção possuem suas próprias referências. Um componente pode citar múltiplas
declarações quando sua composição for realmente necessária. A auditoria examina
cada componente apenas contra as respectivas citações; o input completo não serve
para justificar uma fonte selecionada incorretamente.

Guards declarados em outras fontes devem permanecer separados da permissão:
por exemplo, autorização do autor vem do critério, exigência de identidade/registro
vem das restrições. `target_scope: criteria` exige alvos reais; `project` exige lista
de alvos vazia e pode representar políticas que abrangem outras capacidades.
IDs de alvo indicam aplicabilidade, não são acrescentados como fontes de suporte.

O achado reúne as fontes dos componentes, mas preserva também seus vínculos
individuais e a posição de cada exceção. Pareceres ficam stale se uma fonte muda
de componente, mesmo que texto e união de citações não mudem. Campos desconhecidos,
fontes inelegíveis, colisões de IDs e vínculos inexistentes são rejeitados.

V4 adiciona `component_judgments`, com nome e índice para exceções. O inventário
deve corresponder exatamente aos componentes existentes. Um componente contradito
ou sem evidência suficiente impede supports do achado inteiro. O ledger mantém
todos os vínculos de fontes existentes e diagnostica omissões, como v3.

O host não resolve contradições ou reescreve componentes após a resposta. Guards
são especificações propostas, não controles operacionais implementados. Semântica
continua requerendo revisão; a avaliação humana/holdout permanece num gate posterior.
Os comandos antigos continuam disponíveis e não migram automaticamente para v3/v4.
