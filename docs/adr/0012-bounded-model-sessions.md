# ADR-0012 — Geração supervisionada e avaliação separada

Status: aceito para o segundo incremento da AHC-021.

## Contexto e decisão

O avaliador offline não comprova execução ou identidade de modelo. Sessões reais
precisam de limites de tentativas/tempo e não podem converter geração em qualidade.
Novos contratos aditivos representam plano, resultado do worker e sessão; não
alteramos UnderstandingArtifactEval/v1 nem os contratos do compilador.

O control plane usa JobExecutor e um worker Python próprio em processo separado.
Default: Ollama local instalado, uma tentativa ativa, sem retries; repeats são
execuções independentes contabilizadas. Timeout encerra o worker e interrompe novas
tentativas. Sessão reserva diretório novo, grava plano/jobs e escreve sessão final
por último; journal parcial não é conclusão. Arquivos existentes não são sobrescritos.

SDK fica no adapter/worker. Modelo recebe só UnderstandingRequest: expectativas,
rubrica e revisão não entram no prompt. A identidade observada por tags/show/version
é comparada antes/depois e entre jobs. Modelo/programa/configuração divergentes
interrompem a sessão. Dados do provider são referências, não autenticação.

## Limites

Supervisão limita espera pela chamada; criação do processo, serialização, I/O e
cleanup podem acrescentar tempo. Cleanup tem espera de até 5 s. Não é garantia de
tempo real nem confirmação de que a GPU/servidor interrompeu a requisição após a
conexão morrer; por isso não inicia outro job após timeout.

Nenhum modelo é qualificado por esta sessão. Evals continuam fail/not-run/error;
review independente permanece pendente. Holdout requer opt-in, rubrica com review
declarada e digest do candidato compatível com modelo/programa/configuração fixados.
Isso evita uso acidental, não autentica review ou cegamento do dataset.

Alternativas rejeitadas: confiar só no timeout de leitura HTTP; avaliar sucesso
pela geração; misturar programas/modelos no mesmo relatório; passar expectativas
para o modelo candidato. Referência: [operação](../engineering/model-generation-sessions.md).
