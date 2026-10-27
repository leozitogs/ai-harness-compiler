# Sprint 2.6 — julgamentos humanos dos oito outputs v4

Data: 2026-10-27. Oito julgamentos registrados; correções ainda pendentes.

O PO respondeu à pergunta `call_5288f072466c47ed9a77f17da97d6132`:

- Item 0: **“Li e aprovo os seis casos e vínculos propostos”**.
- Item 1: **“Confirmo a matriz e os vínculos propostos”**.

Ambas as decisões estão vinculadas à proposta de revisão
`03593bf1500e6a84cb88608523003734a3ade87be1970c4de2d2a3edf6cb2c1e` e aos novos
snapshots da [campanha executada](sprint-2-6-v4-development-result.md). Não foram
transferidas aprovações de rodadas anteriores. São declarações humanas recebidas
no chat, sem autenticação criptográfica.

## Resultado registrado

Foram persistidos oito `SemanticHumanReview/v4` e oito novos assessments com
identidades próprias. Resultado: **seis casos PASS, dois FAIL; 45 critérios PASS,
três FAIL e nenhum pendente**. Os vínculos confirmados cobrem 88 achados,
128 componentes e 21 mapeamentos elegíveis; três obrigações continuam sem
mapeamento tipado elegível e não foram preenchidas artificialmente.

| Caso | Resultado revisado | Critérios FAIL |
| --- | --- | --- |
| dev-adversarial-v4 | PASS | Nenhum; rejeição explícita do fragmento e análise legítima preservadas. |
| dev-ambiguous-v4 | FAIL | Cobertura e incerteza. |
| dev-branding-conflict-v4 | PASS | Nenhum; conflito e pergunta de precedência preservados. |
| dev-compatible-rules-v4 | FAIL | Cobertura. |
| dev-new-domain-v4 | PASS | Nenhum; propósito preservado sem nicho inventado. |
| dev-rules-a-v4 | PASS | Nenhum; aprovação necessária sem presumir suficiência. |
| dev-rules-b-v4 | PASS | Nenhum; permissão do autor sem terceiros. “Agente” foi aceito como ator da ação, sem alegar agente de IA ou equivalência com o responsável. |
| dev-unread-assets-v4 | PASS | Nenhum; limitação do asset declarada no artefato. |

No ambíguo, o PO confirmou a cobertura FAIL porque `required-1` exige rule e a
confirmação do operador foi representada como requirement. Confirmou também
incerteza FAIL: `issue-2`, sobre quem é o responsável, não deve bloquear esta
análise de intenção. A obrigação de identidade e a pergunta legítima sobre
condições de conclusão permanecem válidas. Suporte literal, conflitos,
assets e entendimento receberam PASS.

No caso compatível, `required-2` (visibilidade exclusiva) e `required-4`
(revisão/aprovação antes da publicação) continuam sem rule elegível. O conteúdo
literal preservado em requirement não satisfaz esse contrato de cobertura.
Os outros cinco critérios receberam PASS, sem ampliar permissões ou equiparar
responsável e aprovador.

As quatro ocorrências de falha no assessment revisado correspondem às três
obrigações sem cobertura e à pergunta de materialidade inadequada. São três
critérios reprovados, pois duas obrigações pertencem ao mesmo critério no caso
compatível. Nenhum PASS compensa essas falhas.

## Integridade e escopo

[Decisões públicas, resultados e hashes dos novos assessments](../evidence/sprint-2-6-v4-development-20261027/human-review.json).
Revisões integrais e assessments completos permanecem privados. O replay
recalculou os oito resultados e conferiu seus vínculos e arquivos persistidos.
O relatório original da campanha, as respostas, os assessments iniciais,
expectativas e a proposta original não foram reescritos. O snapshot público
anterior conserva seu estado histórico de revisão pendente; este é o registro
subsequente dos julgamentos efetivamente recebidos.

Registrar os julgamentos fez **zero chamadas novas**. O orçamento da campanha
continua consumido e fechado. Seis casos públicos expostos aprovados não
qualificam o modelo em outros projetos nem substituem avaliação independente.
Não há autorização de compilação, promoção de defaults ou fechamento de sprint.

## Pendências de correção

`INC-0031` continua aberto, em draft, sem resolução ou lição verificada. O aceite
confirma o sintoma e os limites de negócio; não demonstra por que o modelo
escolheu os tipos ou a materialidade inadequados.

| Próxima tarefa | Dependência | Verificação exigida |
| --- | --- | --- |
| Especificar distinção entre requisito e regra | Matriz humana acima | Preservar obrigações incondicionais sem gatilhos; representar condições necessárias, permissões, ordem temporal e visibilidade quando sustentadas pelas fontes. Sem regras por ID ou nicho. |
| Especificar materialidade das perguntas | Julgamento do ambíguo | Responsável ainda não identificado não bloqueia por si só a análise de intenção; conflitos reais e condições de conclusão continuam materiais. |
| Implementar candidato corretivo | Especificações e fontes congeladas do candidato anterior | Mudança versionada e regressões offline; não reclassificar expectativas nem reparar respostas históricas. |
| Preparar nova verificação, se necessária | Correção revisável e testes offline | Pedido concreto e orçamento próprios; o registro atual não concede novas chamadas. |

Essas tarefas estão pendentes; não alegamos correção implementada ou melhora
medida. AHC-021/022 e Sprint 2.6 continuam em andamento.
