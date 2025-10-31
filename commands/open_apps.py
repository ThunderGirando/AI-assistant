"""
Comandos para abrir aplicativos
"""
import os
import sys
sys.path.append('../src')
from utils import log_message, open_application, match_command, extract_app_name

def handle_open_command(command, voice):
    """Processa comandos para abrir aplicativos, incluindo múltiplos apps."""
    # Verificar comandos de abrir com tolerância
    is_open_command, matched_word = match_command(command, ['abrir', 'abre', 'abri', 'abrir', 'abrirai', 'abrirporfavor'])
    if not is_open_command:
        return False

    # Extrair todos os nomes de apps do comando
    app_names = extract_multiple_app_names(command, matched_word)

    if not app_names:
        voice.speak("Qual aplicativo você quer abrir?")
        app = voice.listen()
        if app:
            app_names = [app]

    if app_names:
        opened_apps = []
        failed_apps = []

        for app_name in app_names:
            try:
                if open_application(app_name):
                    opened_apps.append(app_name)
                else:
                    failed_apps.append(app_name)
            except Exception as e:
                log_message(f"Erro ao abrir {app_name}: {e}", 'error')
                failed_apps.append(app_name)

        # Responder baseado no resultado
        if opened_apps and not failed_apps:
            if len(opened_apps) == 1:
                voice.speak(f"Abrindo {opened_apps[0]}.")
            else:
                apps_list = ", ".join(opened_apps[:-1]) + " e " + opened_apps[-1] if len(opened_apps) > 1 else opened_apps[0]
                voice.speak(f"Abrindo {apps_list}.")
        elif opened_apps and failed_apps:
            opened_list = ", ".join(opened_apps[:-1]) + " e " + opened_apps[-1] if len(opened_apps) > 1 else opened_apps[0]
            failed_list = ", ".join(failed_apps[:-1]) + " e " + failed_apps[-1] if len(failed_apps) > 1 else failed_apps[0]
            voice.speak(f"Abri {opened_list}, mas não encontrei {failed_list}.")
        else:
            failed_list = ", ".join(failed_apps[:-1]) + " e " + failed_apps[-1] if len(failed_apps) > 1 else failed_apps[0]
            voice.speak(f"Não encontrei {failed_list}.")

    return True
