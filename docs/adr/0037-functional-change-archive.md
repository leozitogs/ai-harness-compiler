# ADR-0037 — Histórico local de mudanças funcionais

Uma mudança pode acumular versões e pareceres ao longo do refinamento. A segunda
fatia de AHC-031 usa um diretório por mudança e uma sequência iniciada em 1.
A identidade do projeto e da mudança permanece estável. Cada entrada reúne
o contrato funcional, seu digest e o digest da versão anterior. A leitura
valida a sequência inteira antes de devolver uma versão.

O operador informa o digest esperado do topo antes de publicar. O arquivo é
gravado e sincronizado em um temporário no próprio diretório. Um hard link
publica a entrada completa de forma exclusiva no destino. Assim, duas
publicações concorrentes para a mesma revisão têm no máximo uma vencedora, sem
manter um índice mutável nem depender de um lock que possa ficar órfão.

Uma declaração de revisão é gravada uma vez por versão. Pode ser anexada a uma
versão histórica se corresponder ao conteúdo exato. Um parecer diferente exige
nova versão. A validação de prontidão continua usando o contrato da primeira fatia.

O diretório é operado localmente em um sistema de arquivos que oferece hard
links. Uma falha de energia pode afetar a durabilidade do diretório. Uma
interrupção abrupta pode deixar um temporário, que é ignorado na leitura.
O histórico detecta divergências internas de conteúdo e encadeamento.
Detectar remoção da cauda ou reescrita coerente requer comparar com um digest
do topo registrado fora do arquivo. O formato guarda snapshots completos e a
leitura percorre o histórico, uma escolha para uso local nesta etapa.
