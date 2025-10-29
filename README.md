# Stark - AI Assistant

![Image](https://github.com/user-attachments/assets/9f90e373-7056-4494-8a5d-21bdee7bb6ca)

Uma IA assistente de voz que executa tarefas no PC, aprende com o usuário e se aprimora sozinha. Desenvolvida em Python com ML/DL.

## Funcionalidades

- **Wake Word Detection**: Ativa ao ouvir "STARK"
- **Reconhecimento de Voz**: Processa comandos em português brasileiro
- **Síntese de Voz**: Responde com voz feminina
- **Abertura de Aplicativos**: Abre Chrome, Notepad, Calculadora, Minecraft, etc.
- **Jogos**: Jogo da velha com IA que aprende
- **Aprendizado de Máquina**: Classifica intenções e aprende com interações
- **Monitoramento de Tela**: Vê a tela em tempo real (baseado em screenshots)
- **Integração com Gemini**: Aprende com comandos desconhecidos usando IA generativa

## Instalação

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure a chave da API do Gemini em `src/config.py` (opcional)

3. Execute:
   ```
   python src/main.py
   ```

## Como Usar

1. Diga "STARK" para ativar
2. Dê comandos como:
   - "STARK abra o chrome"
   - "STARK vamos jogar jogo da velha"
   - "STARK o que você vê?"
   - "STARK sair"

## Estrutura do Projeto

- `src/`: Código fonte
  - `main.py`: Loop principal
  - `voice.py`: Reconhecimento e síntese de voz
  - `learning.py`: Módulo de aprendizado de máquina
  - `vision.py`: Monitoramento de tela
  - `ai_api.py`: Integração com Gemini
  - `config.py`: Configurações
  - `utils.py`: Funções utilitárias
- `games/`: Módulos de jogos
  - `game_module.py`: Jogos disponíveis
- `models/`: Modelos treinados de ML
- `data/`: Dados de treinamento
- `requirements.txt`: Dependências
- `test_microphone.py`: Script de teste do microfone

## Desenvolvimento

- Linguagem: Python 3.x
- Frameworks: speech_recognition, pyttsx3, scikit-learn, tensorflow, pygame
- Plataforma: Windows (compatível com Linux/Mac)

## Próximos Passos

- Melhorar reconhecimento offline
- Adicionar mais jogos
- Integrar com APIs externas
- Aprimorar aprendizado com reinforcement learning

## Licença

MIT License - veja LICENSE para detalhes.
