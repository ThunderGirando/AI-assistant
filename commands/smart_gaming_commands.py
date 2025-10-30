from src.smart_gaming_ai import SmartGamingAI
from src.voice import VoiceAssistant
from src.vision import VisionModule
from src.ai_api import AIAPI
from src.learning_mode import LearningMode
from src.utils import log_message

smart_gaming_ai = SmartGamingAI()

def handle_smart_gaming_command(command, voice, vision, ai, learning_mode, LearningMode):
    """Processa comandos relacionados ao Gaming AI Inteligente."""
    log_message(f"Processando comando de gaming inteligente: {command}")

    if 'iniciar aprendizado inteligente' in command or 'aprender jogo' in command:
        voice.speak("Qual nome você quer dar para esta sessão de aprendizado inteligente?")
        session_name = voice.listen()
        if session_name:
            smart_gaming_ai.start_learning_session(session_name.strip())
            voice.speak(f"Sessão de aprendizado inteligente '{session_name}' iniciada. Jogue normalmente, vou analisar seus padrões.")
        else:
            voice.speak("Não entendi o nome da sessão.")

    elif 'parar aprendizado inteligente' in command or 'finalizar aprendizado' in command:
        smart_gaming_ai.stop_learning_session()
        voice.speak("Sessão de aprendizado finalizada. Treinando modelo inteligente...")

    elif 'jogar inteligente' in command or 'modo inteligente' in command:
        voice.speak("Qual nível de criatividade você quer? Diga um número de 0 a 1, onde 0 é cópia exata e 1 é muito criativo.")
        creativity_response = voice.listen()
        creativity = 0.7  # padrão
        if creativity_response:
            try:
                creativity = float(creativity_response)
                creativity = max(0, min(1, creativity))  # limitar entre 0 e 1
            except:
                pass

        smart_gaming_ai.start_smart_playing(creativity)
        voice.speak(f"Iniciando jogo inteligente com criatividade {creativity}.")

    elif 'parar jogo inteligente' in command or 'parar inteligente' in command:
        smart_gaming_ai.stop_smart_playing()
        voice.speak("Jogo inteligente parado.")

    elif 'analisar jogo' in command or 'o que está acontecendo' in command:
        frame = vision.capture_screen()
        if frame is not None:
            analysis = smart_gaming_ai.analyze_game_context(frame)
            voice.speak(f"Análise: {analysis[:200]}...")  # Limitar tamanho da resposta
        else:
            voice.speak("Não consegui capturar a tela para análise.")

    elif 'ajuda com jogo' in command or 'como jogar' in command:
        voice.speak("Qual é sua dúvida sobre o jogo?")
        question = voice.listen()
        if question:
            frame = vision.capture_screen()
            help_response = smart_gaming_ai.ask_gemini_help(question, frame)
            voice.speak(f"Ajuda: {help_response[:300]}...")  # Limitar tamanho
        else:
            voice.speak("Não entendi sua pergunta.")

    elif 'status inteligente' in command or 'como está o inteligente' in command:
        status = smart_gaming_ai.get_status()
        if status['is_learning']:
            voice.speak(f"Estou aprendendo inteligentemente na sessão '{status['session_name']}'.")
        elif status['is_playing_smart']:
            voice.speak(f"Estou jogando inteligente com criatividade {status['creativity_level']}.")
        else:
            model_status = "Modelo carregado" if status['model_loaded'] else "Modelo não carregado"
            voice.speak(f"Estou parado. {model_status}.")

    else:
        return False  # Comando não reconhecido

    return True
