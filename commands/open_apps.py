"""
Comandos para abrir aplicativos
"""
import os
import sys
sys.path.append('../src')
from utils import log_message, open_application, match_command, extract_app_name

def handle_open_command(command, voice):
    """Processa comandos para abrir aplicativos."""
    # Verificar comandos de abrir com tolerância
    is_open_command, matched_word = match_command(command, ['abrir', 'abre', 'abri', 'abrir', 'abrirai', 'abrirporfavor'])
    if not is_open_command:
        return False

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
        # Extrair nome do app do comando usando a nova função
        app_name = extract_app_name(command, matched_word)
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

    return True
