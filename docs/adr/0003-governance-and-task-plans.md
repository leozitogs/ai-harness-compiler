# ADR-0003 — Governança e planejamento de tarefas observável

Status: aceito para a fundação; Sprint 1 permanece proposta.

O proprietário escolheu Apache-2.0. A distribuição inclui LICENSE e NOTICE;
licenças de inputs, dependências e templates devem ser preservadas separadamente.

Usar monólito modular, branches curtas, Conventional Commits, squash e checks em CI.
Não introduzir `develop` ou microsserviços sem necessidade observada. O primeiro
push é bootstrap; proteção de main deve ser ativada depois de CI válida.

Introduzir TaskGraph como contrato separado da IR do harness, mantendo compatibilidade
dos contratos existentes. Gerar quatro estágios verificáveis por capacidade,
com gates de dependência. Não armazenar raciocínio privado nem declarar execução.

Consequências: plano reproduzível e testável, mas decomposição semântica e estado
durável continuam futuros. O time precisa revisar e refinar as tarefas; geração
automática não constitui compromisso de sprint nem conclusão de critérios.
