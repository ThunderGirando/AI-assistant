"""
Comandos relacionados ao modo de aprendizado
"""
import sys
sys.path.append('../src')
from utils import log_message

def handle_learning_command(command, voice, vision, ai, learning_mode, LearningMode):
    """Processa comandos relacionados ao aprendizado."""
    if 'aprender' in command or 'modo aprendizado' in command or 'começar aprender' in command:
        if not learning_mode:
            learning_mode = LearningMode(voice, vision, ai)
        learning_mode.start_learning()
        voice.speak("Modo de aprendizado ativado! Vou observar sua tela continuamente e fazer perguntas para aprender seus padrões de uso.")
        return True

    elif 'parar aprender' in command or 'parar aprendizado' in command:
        if learning_mode:
            learning_mode.stop_learning()
            voice.speak("Modo de aprendizado desativado.")
        else:
            voice.speak("Modo de aprendizado não está ativo.")
        return True

    elif 'status aprendizado' in command or 'como está o aprendizado' in command:
        if learning_mode:
            status = learning_mode.get_learning_status()
            voice.speak(f"Aprendizado ativo: {status['is_learning']}. Observações: {status['observations_count']}. Perguntas não respondidas: {status['unanswered_questions']}.")
        else:
            voice.speak("Modo de aprendizado não está ativo.")
        return True

    return False
