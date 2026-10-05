# Segurança

Este é um scaffold experimental. O build local lê um manifesto YAML com loader
seguro, valida contratos e exporta arquivos em uma pasta nova. Não chama modelos,
executa o código gerado ou conecta ferramentas externas.

Input de projeto é dado não confiável. Ele é preservado em JSON, separado das
instruções fixas do harness. Essa separação reduz mistura de dados e instruções,
mas não constitui defesa completa contra prompt injection para futuros runtimes.

O manifesto detecta diferenças de bytes; não é assinatura nem validação de segurança.
Políticas geradas não substituem enforcement de permissões em software.
Use exemplos fictícios; não versione credenciais, dados pessoais ou documentos privados.

## Reportar uma falha

Não publique segredos ou uma exploração ativa em uma issue pública.
Use o [canal privado de vulnerabilidades](https://github.com/leozitogs/ai-harness-compiler/security/advisories/new)
habilitado no GitHub. Inclua versão afetada, reprodução mínima sem dados privados,
impacto e mitigação conhecida. O mantenedor inicial é @leozitogs; ainda não há
prazo de resposta garantido ou programa de recompensas.
