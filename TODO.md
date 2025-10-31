# TODO: Integrar Comando Direto Gemini no Stark AI

## Tarefas Principais
- [x] Remover dependência gpt4all de requirements.txt
- [x] Remover arquivos src/gpt4all_integration.py e tests/test_gpt4all.py
- [x] Modificar src/ai_api.py para usar apenas Gemini (sem fallback local)
- [x] Otimizar configuração Gemini para modelos gratuitos mais rápidos (Gemini 2.0 Flash)
- [x] Atualizar src/config.py com configurações otimizadas para Gemini
- [x] Testar integração direta com Gemini no assistente Stark
- [x] Limpar arquivos de cache GPT4All
- [x] Atualizar README.md removendo referências a modelos locais
- [x] Fixar persona para Stark (remover Frieren)
- [x] Adicionar medição de tempo de resposta

## Nova Feature: Comando Direto Gemini
- [x] Adicionar detecção de comando "stark ... gemini [query]" em src/core.py
- [x] Implementar extração da query após "gemini"
- [x] Criar método em ai_api.py para adaptar query em pergunta real usando IA
- [x] Integrar chamada direta ao Gemini sem cache para comandos "gemini"
- [x] Testar comando de voz "stark pergunte ao gemini quanto é 1+1"
- [x] Atualizar documentação no README.md

## Nova Feature: Modo Chat Multi-Turn
- [x] Implementar sessão de chat persistente em ai_api.py
- [x] Adicionar métodos start_chat_session, end_chat_session, is_chat_mode_active, send_chat_message
- [x] Integrar comandos de chat em core.py ("vamos conversar", "sair do chat")
- [x] Modificar _fallback_to_ai para detectar modo chat ativo
- [x] Testar conversas naturais multi-turn
- [x] Atualizar documentação no README.md

## Motivo da Mudança
- GPT4All local: 109.93s para resposta simples (muito lento)
- Gemini API direta: Respostas rápidas, gratuitas até limites generosos
- Melhor experiência do usuário com velocidade
- Menos complexidade no código

## Modelos Gemini Gratuitos Prioritários
1. Gemini 2.0 Flash: Mais rápido e atual (atual)
2. Gemini 1.5 Flash: Backup rápido para tarefas simples
3. Gemini 1.5 Pro: Para tarefas complexas quando necessário

## Estratégia Comando Gemini
1. Detectar palavra-chave "gemini" no comando
2. Extrair texto após "gemini" como query bruta
3. Usar IA para transformar em pergunta real (ex: "quanto é 1+1" -> "Qual é o resultado de 1 + 1?")
4. Chamar Gemini diretamente sem cache
5. Retornar resposta formatada
