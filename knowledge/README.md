# Memória de engenharia

Comece pelo [índice gerado](INDEX.md) e pelo
[manual de operação](../docs/engineering/memory-system.md).

Registros DE, DOC, ADR, INC, LES, RUN e EXP são contratos versionados em `records/`.
Cada nova revisão acrescenta um JSON, preservando decisões e experiências anteriores.
Templates em `templates/` servem como ponto de partida; substituir seus exemplos.

```sh
uv run factory memory search "problema ou decisão"
uv run factory memory check
uv run factory memory index --check
```

Esta memória atende o próprio projeto, colaboradores via chat e especialistas
locais/Ollama. Consulta não altera pesos de modelos. Drafts não são recomendações
validadas, e evidências desatualizadas excluem registros da recuperação padrão.

A futura Engineering Knowledge Base de padrões multi-domínio deverá usar
proveniência, licença e escopo equivalentes, sem concatenar o corpus ao contexto.
