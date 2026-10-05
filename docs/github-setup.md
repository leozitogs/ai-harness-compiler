# Configuração do repositório no GitHub

**Repository name**

```text
ai-harness-compiler
```

**Display name**

```text
AI Harness Compiler
```

**Description**

```text
Compile project intent into typed, verifiable AI engineering harnesses: architecture, context, prompts, skills, tools, workflows, guardrails, and evals.
```

A description descreve a visão do produto; o README delimita o estágio atual.

**Topics sugeridos**

```text
ai-engineering, harness-engineering, compiler, llm, agentic-ai,
context-engineering, evals, mcp, python, pydantic
```

## Criar e publicar

Crie no GitHub um repositório vazio chamado `ai-harness-compiler`.
Escolha a visibilidade desejada. Não marque geração automática de README,
.gitignore ou licença: os dois primeiros já existem; a licença ainda precisa ser escolhida.

O Git local já foi inicializado na branch `main`. Após revisar os arquivos:

```sh
git add .
git commit -m "chore: bootstrap AI Harness Compiler"
git remote add origin https://github.com/SEU_USUARIO/ai-harness-compiler.git
git push -u origin main
```

Substitua `SEU_USUARIO`. Nenhum remote, commit ou push faz parte da criação deste scaffold.
Depois da primeira execução da CI, configure proteção de `main` conforme seu fluxo.
Se o GitHub disponibilizar private vulnerability reporting para esse repo, habilite-o.
Escolha a licença de distribuição antes de anunciar o projeto como open source.
