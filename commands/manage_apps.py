"""
Comandos para gerenciar aplicativos (adicionar, listar)
"""
import sys
sys.path.append('../src')
from utils import log_message, add_application, load_apps

def handle_add_app_command(command, voice):
    """Processa comando para adicionar aplicativo."""
    if 'adicionar' in command and 'aplicativo' in command:
        voice.speak("Digite o nome do aplicativo no terminal e pressione Enter.")
        app_name = input("Nome do aplicativo: ").strip()
        if app_name:
            voice.speak("Agora digite o caminho completo do executável e pressione Enter.")
            app_path = input("Caminho do aplicativo: ").strip()
            if app_path:
                add_application(app_name, app_path)
                voice.speak(f"Aplicativo {app_name} adicionado com sucesso!")
            else:
                voice.speak("Caminho vazio. Tente novamente.")
        else:
            voice.speak("Nome vazio. Tente novamente.")
        return True
    return False

def handle_list_apps_command(command, voice):
    """Processa comando para listar aplicativos."""
    if 'listar' in command and 'aplicativos' in command:
        apps = load_apps()
        if apps:
            app_list = ", ".join(apps.keys())
            print(f"Aplicativos cadastrados: {app_list}")
            voice.speak(f"Você tem {len(apps)} aplicativos cadastrados. Veja a lista no terminal.")
        else:
            voice.speak("Nenhum aplicativo cadastrado ainda.")
        return True
    return False
