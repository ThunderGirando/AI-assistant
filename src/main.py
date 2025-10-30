import threading
import time
import sys
import os

# Adicionar o diretório raiz ao path para encontrar commands/
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from voice import VoiceAssistant
from vision import VisionModule
from ai_api import AIAPI
from voice_recognition import VoiceRecognition
from learning_mode import LearningMode
from utils import setup_logging, log_message
from config import WAKE_WORD
from commands import open_apps, manage_apps, vision_commands, learning_commands

# Configurar logging com rotação
setup_logging()

def handle_command(command, voice, vision, ai, voice_recog=None, learning_mode=None):
    """Processa um comando."""
    log_message(f"Processando comando: {command}")
    context = vision.get_screen_context()

    # Verificar se é resposta de aprendizado
    if learning_mode and learning_mode.questions_queue:
        unanswered = [q for q in learning_mode.questions_queue if not q['answered']]
        if unanswered:
            # Processar como resposta de aprendizado
            if learning_mode.process_learning_response(command):
                voice.speak("Obrigado pela resposta! Continuando a aprender...")
                return True

    # Tentar comandos organizados por módulos
    if open_apps.handle_open_command(command, voice):
        return True

    if manage_apps.handle_add_app_command(command, voice):
        return True

    if manage_apps.handle_list_apps_command(command, voice):
        return True

    if vision_commands.handle_vision_command(command, voice, vision, learning_mode, LearningMode, ai):
        return True

    if learning_commands.handle_learning_command(command, voice, vision, ai, learning_mode, LearningMode):
        return True

    # Comandos básicos que ficam na main
    if 'gravar voz' in command or 'treinar voz' in command:
        voice.speak("Vou gravar algumas amostras da sua voz para reconhecimento. Diga 'pronto' quando estiver pronto.")
        ready = voice.listen()
        if ready and 'pronto' in ready:
            voice.speak("Gravando primeira amostra... diga 'STARK'.")
            voice_recog.record_voice_sample('user')
            voice.speak("Segunda amostra... diga 'STARK' novamente.")
            voice_recog.record_voice_sample('user')
            voice.speak("Terceira amostra... diga 'STARK' mais uma vez.")
            voice_recog.record_voice_sample('user')
            voice.speak("Treinando modelo de reconhecimento de voz...")
            if voice_recog.train_voice_model('user'):
                voice.speak("Modelo treinado com sucesso! Agora reconheço sua voz.")
            else:
                voice.speak("Não foi possível treinar o modelo. Tente novamente com mais amostras.")
        return True

    elif 'sair' in command or 'parar' in command:
        voice.speak("Até logo!")
        return False

    else:
        # Usar IA para comandos desconhecidos
        response = ai.learn_from_unknown(command, context)
        voice.speak(response)

    return True

def main():
    voice = VoiceAssistant()
    vision = VisionModule()
    ai = AIAPI()
    voice_recog = VoiceRecognition()
    learning_mode = None  # Inicializar como None

    log_message("Sistema STARK iniciado. Diga 'STARK' para me chamar.")
    voice.speak("Sistema STARK iniciado. Diga 'STARK' para me chamar.")

    # Iniciar monitoramento de tela em thread separada (sem logs constantes)
    def monitor_screen():
        vision.continuous_monitoring(lambda ctx: None)  # Sem logging constante

    monitor_thread = threading.Thread(target=monitor_screen, daemon=True)
    monitor_thread.start()

    while True:
        # Verificar se há perguntas de aprendizado pendentes
        if learning_mode and learning_mode.questions_queue:
            unanswered = [q for q in learning_mode.questions_queue if not q['answered']]
            if unanswered:
                # Modo de resposta de aprendizado - ouvir continuamente sem wake word
                log_message("Aguardando resposta de aprendizado...")
                voice.speak("Estou ouvindo sua resposta...")
                response = voice.listen(timeout=10)  # Timeout de 10 segundos para resposta
                if response:
                    log_message(f"Resposta de aprendizado recebida: {response}")
                    if learning_mode.process_learning_response(response):
                        voice.speak("Obrigado pela resposta! Continuando a aprender...")
                    else:
                        voice.speak("Não entendi sua resposta. Tente novamente.")
                else:
                    voice.speak("Não ouvi resposta. Continuando observação...")
                continue  # Voltar para verificar se ainda há perguntas pendentes

        # Modo normal - aguardar wake word
        command = voice.listen_for_wake_word()
        if command:
            if not handle_command(command, voice, vision, ai, voice_recog, learning_mode):
                break

if __name__ == "__main__":
    main()
