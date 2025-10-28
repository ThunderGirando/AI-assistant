# Frieren AI Assistant

Uma IA assistente inspirada em Frieren, a maga elfa de Sousou no Frieren. Ela responde ao comando de voz "Frieren", pode abrir aplicativos no PC e monitorar a tela em tempo real.

## Funcionalidades

- **Wake Word Detection**: Ativa ao ouvir "Frieren"
- **Reconhecimento de Voz**: Processa comandos em português
- **Síntese de Voz**: Responde com voz feminina
- **Abertura de Aplicativos**: Abre Chrome, Notepad, Calculadora, etc.
- **Monitoramento de Tela**: Vê a tela em tempo real (baseado em screenshots)
- **Integração com Gemini**: Aprende com comandos desconhecidos usando IA generativa

## Instalação

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure a chave da API do Gemini em `src/config.py`

3. Execute:
   ```
   python src/main.py
   ```

## Como Usar

1. Diga "Frieren" para ativar
2. Dê comandos como:
   - "Abrir Chrome"
   - "Abrir Calculadora"
   - "O que você vê?"
   - "Sair"

## Estrutura do Projeto

- `src/`: Código fonte
  - `main.py`: Loop principal
  - `voice.py`: Reconhecimento e síntese de voz
  - `vision.py`: Monitoramento de tela
  - `ai_api.py`: Integração com Gemini
  - `config.py`: Configurações
  - `utils.py`: Funções utilitárias
- `models/`: Modelos de ML (futuro)
- `data/`: Dados de treinamento (futuro)
- `requirements.txt`: Dependências

## Licença

MIT License - veja LICENSE para detalhes.
