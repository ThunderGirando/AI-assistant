# Stark AI Assistant

![Image](https://github.com/user-attachments/assets/ee0facb1-d380-4e8b-b1c9-2443763bbe22)

Um assistente de IA inteligente que combina visão computacional, reconhecimento de voz e aprendizado de máquina para criar uma experiência interativa completa.

## Funcionalidades

- **Reconhecimento de Voz**: Ativação por palavra-chave "stark"
- **Visão Computacional**: Análise de tela em tempo real
- **IA Conversacional**: Respostas rápidas usando Gemini API direta + suporte futuro ao Ollama local
- **Cache Inteligente**: Respostas instantâneas para perguntas frequentes
- **Suporte a Jogos**: Integração com dados de jogos
- **Interface Amigável**: Design intuitivo e responsivo

## Instalação

### Pré-requisitos

- Python 3.8+
- Chave da API Gemini gratuita (Google AI Studio)
- Microfone para reconhecimento de voz
- Webcam para visão computacional

### Passos de Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/stark-ai-assistant.git
   cd stark-ai-assistant
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure a API Key**:
   - Obtenha uma chave gratuita em [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Edite o arquivo `src/config.py`
   - Substitua `'YOUR_GEMINI_API_KEY'` pela sua chave

4. **(Opcional) Instale Ollama para IA Local**:
   - Baixe e instale Ollama: https://ollama.ai/download
   - Execute: `ollama pull mistral:7b` (ou outro modelo de sua preferência)
   - O assistente detectará automaticamente e usará como fallback

5. **Execute o assistente**:
   ```bash
   python run.py
   ```

## Configuração

### Modelos Gemini Gratuitos Disponíveis

Baseado na API do Google AI Studio, os modelos gratuitos incluem:
- **Gemini 2.0 Flash**: Mais rápido e atual (recomendado)
- **Gemini 1.5 Flash**: Backup rápido para tarefas simples
- **Gemini 1.5 Pro**: Para tarefas mais complexas quando necessário

### Configurações de Voz

- **Idioma**: Português brasileiro (pt-BR)
- **Velocidade**: 200 palavras por minuto
- **Volume**: 100%
- **Palavra de ativação**: "stark"

### Configurações de IA

- **API Direta**: Conexão direta com Gemini (sem intermediários)
- **Cache**: Sistema inteligente para respostas rápidas
- **Limites**: Respeita automaticamente os limites gratuitos
- **Ollama**: Suporte futuro para modelos locais (Mistral, Llama, etc.)

## Uso

### Comandos Básicos

- **"Stark"**: Ativa o assistente
- **"O que você pode fazer?"**: Lista de funcionalidades
- **"Conte uma piada"**: Respostas divertidas
- **"Qual é o clima?"**: Informações sobre o tempo
- **"Me ajude com programação"**: Assistência em código

### Comando Gemini Direto

Use "STARK gemini [pergunta]" para consultar diretamente o Gemini:

- **"STARK gemini quanto é 1+1"**: Resposta direta do Gemini
- **"STARK gemini qual é a capital da França"**: Perguntas factuais
- **"STARK gemini explique a teoria da relatividade"**: Explicações complexas

**Importante**: Ao usar "gemini", o modo chat é ativado automaticamente, permitindo conversas naturais sem precisar dizer "STARK" novamente.

O comando funciona assim:
1. Detecta "gemini" no comando
2. Ativa automaticamente o modo chat
3. Extrai a pergunta após a palavra
4. Adapta para pergunta clara usando IA
5. Consulta Gemini diretamente (sem cache)
6. Retorna resposta completa e mantém conversa ativa

### Modo Chat Multi-Turn

Para conversas naturais e contextuais:

- **"STARK vamos conversar"**: Ativa o modo chat
- **"STARK sair do chat"**: Desativa o modo chat

Comandos para encerrar o chat (aceita variações naturais):
- "sair do chat", "parar conversa", "encerrar chat"
- "pode fechar o chat", "pode parar a conversa"
- "ta bom", "pode parar", "chega", "encerra", "para", "para ai", "para com isso", "fecha o chat"

No modo chat:
- **Não é necessário dizer "STARK" novamente** - o assistente fica ouvindo continuamente
- Conversas são mantidas em contexto
- Respostas são mais naturais e contextuais
- Suporte a follow-ups e esclarecimentos
- Histórico de conversa preservado durante a sessão

Exemplo de uso:
```
Usuário: "STARK vamos conversar"
Stark: "Modo conversa ativado! Agora podemos conversar naturalmente."

Usuário: "me conte uma história" (sem STARK)
Stark: "Que tipo de história você gostaria? Aventura, ficção científica, ou algo engraçado?"

Usuário: "aventura" (sem STARK)
Stark: "Era uma vez, em uma floresta misteriosa..."

Usuário: "ta bom" (ou "pode parar", "chega", etc.)
Stark: "Modo conversa encerrado."
```

### Comandos Avançados

- **Análise de tela**: "O que você vê na minha tela?"
- **Jogos**: "Me fale sobre jogos"
- **Aprendizado**: O assistente aprende com suas interações
- **Estatísticas**: "estatísticas" ou "stats" para ver uso da API

## Arquitetura Simplificada

```
stark-ai-assistant/
├── run.py                  # Ponto de entrada principal
├── src/
│   ├── core.py             # Lógica central (StarkCore)
│   ├── ai_api.py           # API Gemini + suporte Ollama
│   ├── voice.py            # Reconhecimento e síntese de voz
│   ├── vision.py           # Visão computacional
│   ├── voice_recognition.py # Treinamento de voz
│   ├── utils.py            # Utilitários e logging
│   └── config.py           # Configurações
├── commands/               # Comandos organizados por módulo
├── cache/                  # Cache de respostas
├── data/                   # Dados (apps, voice samples, etc.)
├── requirements.txt        # Dependências
└── README.md              # Documentação
```

## Desenvolvimento

### Principais Mudanças Recentes

- **Integração Ollama**: Suporte para modelos locais (Mistral 7B, Llama 3, etc.)
- **Performance**: API Gemini direta para respostas rápidas
- **Confiabilidade**: Menos dependências, mais estabilidade
- **Custo**: Totalmente gratuito (dentro dos limites)
- **Arquitetura**: Refatoração para StarkCore com threads

### Testes

Execute os testes com:
```bash
python -m pytest tests/
```

## Limitações

- Requer conexão com internet para Gemini API
- Dependente de hardware (microfone, câmera)
- Limites de uso da API Gemini gratuita
- Idioma principal: português brasileiro

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
