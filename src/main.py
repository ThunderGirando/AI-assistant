import threading
from voice import VoiceAssistant
from vision import VisionModule
from ai_api import AIAPI
from voice_recognition import VoiceRecognition
from utils import log_message, open_application
from config import WAKE_WORD

def handle_command(command, voice, vision, ai, voice_recog=None):
    """Processa um comando."""
    log_message(f"Processando comando: {command}")
    context = vision.get_screen_context()

    if 'abrir' in command:
        if 'chrome' in command or 'navegador' in command:
            try:
                open_application('chrome.exe')
                voice.speak("Abrindo Chrome.")
            except Exception as e:
                log_message(f"Erro ao abrir Chrome: {e}", 'error')
                voice.speak("Não sei onde está o Chrome. Qual é o caminho completo?")
                path = voice.listen()
                if path:
                    open_application(path)
                    voice.speak("Tentando abrir.")
        elif 'notepad' in command or 'bloco de notas' in command:
            try:
                open_application('notepad.exe')
                voice.speak("Abrindo Bloco de Notas.")
            except Exception as e:
                log_message(f"Erro ao abrir Notepad: {e}", 'error')
                voice.speak("Não sei onde está o Notepad. Qual é o caminho completo?")
                path = voice.listen()
                if path:
                    open_application(path)
                    voice.speak("Tentando abrir.")
        elif 'calculadora' in command:
            try:
                open_application('calc.exe')
                voice.speak("Abrindo Calculadora.")
            except Exception as e:
                log_message(f"Erro ao abrir Calculadora: {e}", 'error')
                voice.speak("Não sei onde está a Calculadora. Qual é o caminho completo?")
                path = voice.listen()
                if path:
                    open_application(path)
                    voice.speak("Tentando abrir.")
        elif 'minecraft' in command or 'mine' in command:
            try:
                open_application(r'C:\XboxGames\Minecraft Launcher\Content\Minecraft.exe')  # Caminho fornecido pelo usuário
                voice.speak("Abrindo Minecraft.")
            except Exception as e:
                log_message(f"Erro ao abrir Minecraft: {e}", 'error')
                voice.speak("Não encontrei o Minecraft. Qual é o caminho completo?")
                path = voice.listen()
                if path:
                    open_application(path)
                    voice.speak("Tentando abrir.")
        else:
            voice.speak("Qual aplicativo você quer abrir?")
            app = voice.listen()
            if app:
                try:
                    open_application(app)
                    voice.speak(f"Tentando abrir {app}.")
                except Exception as e:
                    log_message(f"Erro ao abrir {app}: {e}", 'error')
                    voice.speak(f"Não sei onde está {app}. Qual é o caminho completo?")
                    path = voice.listen()
                    if path:
                        open_application(path)
                        voice.speak("Tentando abrir.")
    elif 'gravar voz' in command or 'treinar voz' in command:
        voice.speak("Vou gravar algumas amostras da sua voz para reconhecimento. Diga 'pronto' quando estiver pronto.")
        ready = voice.listen()
        if ready and 'pronto' in ready:
            voice.speak("Gravando primeira amostra... diga 'Frieren'.")
            voice_recog.record_voice_sample('user')
            voice.speak("Segunda amostra... diga 'Frieren' novamente.")
            voice_recog.record_voice_sample('user')
            voice.speak("Terceira amostra... diga 'Frieren' mais uma vez.")
            voice_recog.record_voice_sample('user')
            voice.speak("Treinando modelo de reconhecimento de voz...")
            if voice_recog.train_voice_model('user'):
                voice.speak("Modelo treinado com sucesso! Agora reconheço sua voz.")
            else:
                voice.speak("Não foi possível treinar o modelo. Tente novamente com mais amostras.")
    elif 'ver tela' in command or 'o que você vê' in command:
        voice.speak(f"Estou vendo: {context}")
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

    log_message("Sistema Frieren iniciado. Diga 'Frieren' para me chamar.")
    voice.speak("Sistema Frieren iniciado. Diga 'Frieren' para me chamar.")

    # Iniciar monitoramento de tela em thread separada (sem logs constantes)
    def monitor_screen():
        vision.continuous_monitoring(lambda ctx: None)  # Sem logging constante

    monitor_thread = threading.Thread(target=monitor_screen, daemon=True)
    monitor_thread.start()

    while True:
        command = voice.listen_for_wake_word()
        if command:
            if not handle_command(command, voice, vision, ai, voice_recog):
                break

if __name__ == "__main__":
    main()
