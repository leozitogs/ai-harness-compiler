# Sprint 2.6 — Revisão humana do desenvolvimento concluída

Data: 2026-10-20. Escopo: oito respostas históricas selecionadas, não o candidato v3.2.

O PO julgou explicitamente todos os seis critérios de cada resposta, após as
perguntas objetivas e acesso às fontes/respostas completas. Foram preservadas
as declarações `human-declared-not-authenticated`, sem alegar autenticação externa.

| Resposta | Cobertura | Suporte | Conflitos | Assets | Incerteza | Entendimento | Resultado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dev-adversarial | pass | pass | pass | pass | pass | pass | pass |
| dev-ambiguous | fail | fail | pass | pass | pass | pass | fail |
| dev-branding-conflict | pass | fail | pass | pass | pass | pass | fail |
| dev-compatible-rules — recuperação | pass | pass | pass | pass | pass | pass | pass |
| dev-new-domain | pass | pass | pass | pass | pass | pass | pass |
| dev-rules-a | pass | pass | pass | pass | pass | pass | pass |
| dev-rules-b | fail | fail | pass | pass | pass | pass | fail |
| dev-unread-assets | pass | pass | pass | pass | pass | pass | pass |

**48 critérios julgados: 43 pass e 5 fail. Cinco respostas pass e três fail.**
Falhas não são compensadas por médias. Não há qualificação de modelo, aceite
de histórias ou autorização de compilação derivada desses resultados.

## Evidência e limites aceitos pelo PO

O [manifesto completo](../evidence/sprint-2-6-development-assessment-20261020/manifest.json)
vincula cada caso, rubrica, análise, declaração humana, assessment e fontes físicas
por hash. Os inventários completos de cobertura, achados e componentes são
revalidados pelo contrato v3 e pelos testes. As revisões parciais anteriores e a
tentativa original com erro estrutural continuam intactas. O pass de regras
compatíveis pertence somente à recuperação v3.1, não à tentativa original.

O PO aceitou explicitamente dois limites de representação:

- No caso adversarial, identidade preservada como capability é suficiente nesta
  análise de intenção; isso não comprova um controle executável.
- No caso do asset não lido, a limitação declarada nos metadados/átomos do artefato
  é suficiente, sem repetição obrigatória nos achados interpretativos. O arquivo
  não foi ingerido e seu conteúdo não foi afirmado.

O domínio novo e a regra de aprovação designada receberam aceite específico de
todos os critérios. O PO também confirmou a matriz negativa dos três casos abaixo,
incluindo quais critérios permanecem corretos. Esses julgamentos não vieram de
contar alertas do auditor nem de sucesso estrutural do JSON.

## Falhas confirmadas e encaminhamento

1. **Ambiguidade:** `guard-1` condiciona identificação a registrar decisões de
   publicação sem evidência dessa aplicabilidade. Cobertura e suporte fail;
   a confirmação do operador e as perguntas materiais continuam válidas.
2. **Autor sem terceiros:** `guard-1` vincula a identificação à liberação pelo
   autor sem fonte para essa relação. Preservar a permissão sem aprovação extra
   não basta para validar a aplicabilidade adicionada. Cobertura e suporte fail.
3. **Conflito branding/backlog:** o conflito possui as duas fontes, mas a pergunta
   `uncertainty-1-1` menciona as duas declarações citando apenas o backlog.
   O contexto global não corrige o inventário da própria pergunta. Suporte fail.

A variante v3.2 já preparada aborda os dois primeiros problemas como hipótese
corretiva, sem novas gerações ou eficácia demonstrada. O terceiro exige preservar
as duas fontes também na pergunta; uma opção de desenvolvimento é usar uma issue
com os índices de ambas, evitando a pergunta local que herda só o critério.
Essa alternativa ainda precisa ser implementada e verificada; não há repair
automático dos relatórios históricos.

## Próximo trabalho e gates

- AHC-021: revisar o incremento/evidências e os critérios de entrega da história;
  a pendência de julgamento destas oito respostas foi resolvida.
- AHC-022: preparar correção generalista da pergunta com múltiplas fontes,
  congelar receita/candidato e planejar comparação de desenvolvimento com todas
  as tentativas registradas. Não atribuir estes resultados à receita v3.2.
- Antes de chamar o modelo: fixar budget e protocolo concretos, sem trocar modelo,
  parâmetros ou contexto silenciosamente. Nenhum holdout foi aberto.
- AHC-024/025/026 não são liberadas automaticamente pela matriz; permanecem
  sujeitas à revisão das dependências e aos seus próprios gates.

Os testes padrão apenas reproduzem os vínculos e julgamentos declarados.
Não fazem novas chamadas nem medem uma taxa de acerto generalizável.
