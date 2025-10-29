import threading
import time
from voice import VoiceAssistant
from vision import VisionModule
from ai_api import AIAPI
from voice_recognition import VoiceRecognition
from utils import log_message, open_application
from config import WAKE_WORD
import os

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
                if open_application('minecraft'):
                    voice.speak("Abrindo Minecraft.")
                else:
                    voice.speak("Não encontrei o Minecraft. Qual é o caminho completo?")
                    path = voice.listen()
                    if path:
                        try:
                            os.startfile(path)
                            voice.speak("Tentando abrir.")
                        except Exception as e2:
                            log_message(f"Erro ao abrir caminho alternativo: {e2}", 'error')
                            voice.speak("Não consegui abrir.")
            except Exception as e:
                log_message(f"Erro ao abrir Minecraft: {e}", 'error')
                voice.speak("Não encontrei o Minecraft. Qual é o caminho completo?")
                path = voice.listen()
                if path:
                    try:
                        os.startfile(path)
                        voice.speak("Tentando abrir.")
                    except Exception as e2:
                        log_message(f"Erro ao abrir caminho alternativo: {e2}", 'error')
                        voice.speak("Não consegui abrir.")
        else:
            # Extrair nome do app do comando (ex: "abrir opera" -> "opera")
            app_name = command.replace('abrir', '').strip()
            if app_name:
                try:
                    if open_application(app_name):
                        voice.speak(f"Abrindo {app_name}.")
                    else:
                        voice.speak(f"Não encontrei {app_name}. Qual é o caminho completo?")
                        path = voice.listen()
                        if path:
                            try:
                                os.startfile(path)
                                voice.speak("Tentando abrir.")
                            except Exception as e2:
                                log_message(f"Erro ao abrir {path}: {e2}", 'error')
                                voice.speak("Não consegui abrir.")
                except Exception as e:
                    log_message(f"Erro ao abrir {app_name}: {e}", 'error')
                    voice.speak(f"Não sei onde está {app_name}. Qual é o caminho completo?")
                    path = voice.listen()
                    if path:
                        try:
                            os.startfile(path)
                            voice.speak("Tentando abrir.")
                        except Exception as e2:
                            log_message(f"Erro ao abrir {path}: {e2}", 'error')
                            voice.speak("Não consegui abrir.")
            else:
                voice.speak("Qual aplicativo você quer abrir?")
                app = voice.listen()
                if app:
                    try:
                        if open_application(app):
                            voice.speak(f"Abrindo {app}.")
                        else:
                            voice.speak(f"Não encontrei {app}.")
                    except Exception as e:
                        log_message(f"Erro ao abrir {app}: {e}", 'error')
                        voice.speak(f"Não sei onde está {app}.")
    elif 'adicionar' in command and 'aplicativo' in command:
        voice.speak("Digite o nome do aplicativo no terminal e pressione Enter.")
        app_name = input("Nome do aplicativo: ").strip()
        if app_name:
            voice.speak("Agora digite o caminho completo do executável e pressione Enter.")
            app_path = input("Caminho do aplicativo: ").strip()
            if app_path:
                from utils import add_application
                add_application(app_name, app_path)
                voice.speak(f"Aplicativo {app_name} adicionado com sucesso!")
            else:
                voice.speak("Caminho vazio. Tente novamente.")
        else:
            voice.speak("Nome vazio. Tente novamente.")
    elif 'gravar voz' in command or 'treinar voz' in command:
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
    elif 'listar' in command and 'aplicativos' in command:
        from utils import load_apps
        apps = load_apps()
        if apps:
            app_list = ", ".join(apps.keys())
            print(f"Aplicativos cadastrados: {app_list}")
            voice.speak(f"Você tem {len(apps)} aplicativos cadastrados. Veja a lista no terminal.")
        else:
            voice.speak("Nenhum aplicativo cadastrado ainda.")
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

    log_message("Sistema STARK iniciado. Diga 'STARK' para me chamar.")
    voice.speak("Sistema STARK iniciado. Diga 'STARK' para me chamar.")

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
