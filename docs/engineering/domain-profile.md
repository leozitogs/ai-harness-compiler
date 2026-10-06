# AHC-002 — Perfil multidimensional

`DomainProfile/v1` representa classificação, arquétipo, dados, riscos e alternativas.
O core preserva informações fornecidas: não pesquisa fontes, chama modelos ou
deduz classificação a partir de palavras do backlog.

| Dimensão | Contrato |
|---|---|
| Domínio | primary opcional e secondary sem duplicatas/repetição do primary |
| Arquétipo | Texto extensível, sem taxonomia fechada artificial |
| Dados | data_types únicos, sensitivity e contains_pii (bool ou desconhecido) |
| Risco | level e categorias de privacidade, segurança, regulação, alucinação, agência, disponibilidade e custo |
| Classificação | status, origin, rationale e evidências |
| Alternativas | hipóteses com domínio, justificativa e referências de domínio |

## Estados e incerteza

- `declared` + `user-declaration`: primary e evidências obrigatórios.
- `hypothesis` + `supplied-hypothesis`: primary, evidências e justificativa obrigatórios.
- `DOMAIN_UNCERTAIN` + `unknown`: primary deve ser null; alternativas não são
  selecionadas automaticamente. Dimensões fornecidas podem existir sem resolver primary.

Confidence é **null em todos os estados**. Um número sem avaliação/calibração
independente não é confiança válida. Um futuro classificador precisará evoluir o
contrato com método, dataset e resultados, antes de emitir scores.

Campos ausentes permanecem desconhecidos: arquétipo null, sensibilidade e risco
unknown, contains_pii null. Esses valores não equivalem a baixo risco ou ausência
de dados pessoais. Categorias/extensões textuais não provam aderência regulatória.

## Entrada e proveniência

`ProjectInput/v1` recebe `domain_profile` opcional. O campo antigo `domain` segue
aceito: produz perfil declared, com dimensões ausentes desconhecidas. Se ambos
forem fornecidos, o novo perfil deve declarar o mesmo primary; contradições e
rebaixamento de declaração para hipótese são rejeitados.

```sh
factory validate examples/domain-profile
factory build examples/domain-profile --output output/domain-demo
factory schema domain-profile
```

O [exemplo](../../examples/domain-profile/project.yaml) contém hipótese fictícia.
A evidência reservada `domain-profile` aponta a `project.yaml#/domain_profile`
e preserva o perfil completo como declaração de quem forneceu a hipótese. Isso
registra a proposta; não afirma que o domínio proposto é verdadeiro.

Perfis podem citar evidências externas fornecidas no Evidence Pack, sempre com
scope domain e fonte não rejeitada. Declared exige evidências declared; alternativas
podem citar pesquisa ou derivações. IDs repetidos na mesma lista são rejeitados;
alternativas diferentes podem compartilhar a fonte. Todo perfil e referência é
revalidado antes da emissão. A IR não pode acrescentar dimensões ausentes do input.

## Compatibilidade e migração

IR atual: **ProjectDNA/v3 + HarnessSpec/v3**. EvidencePack/v1, CapabilityGraph/v1
e TaskGraph/v1 mantêm os contratos. Manifestos antigos válidos continuam aceitos
pelo compilador atual; leitores antigos com extra forbid precisam de atualização
para usar o novo campo opcional.

```sh
factory migrate tests/fixtures/harness-v1.json --output output/from-v1.json
factory migrate tests/fixtures/harness-v2.json --output output/from-v2.json
factory compile output/from-v2.json --output output/from-v2-build
```

Migração exige destino novo e diretório pai existente. Declarações são preservadas,
dimensões ausentes são preenchidas como desconhecidas. Não inventar dados, risco,
arquétipo ou scores. O digest da fonte canônica v2 é validado usando o input sem
o novo campo e recalculado para o snapshot v3, que inclui domain_profile null.
Fontes externas e seus metadados são preservados.

Confidence numérica antiga sem proveniência, status inválido, digest adulterado ou
fonte canônica revisada exigem migração manual. A migração automática não atribui
aprovação antiga a um digest novo. IR v1 com evidências customizadas continua
exigindo proveniência manual, conforme o contrato do Evidence Pack.
