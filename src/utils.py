import os
import subprocess
import logging
import json
import difflib
from config import LOG_FILE, DEBUG_MODE

# Configurar logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG if DEBUG_MODE else logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_message(message, level='info'):
    """Registra uma mensagem no log e no console."""
    print(f"[{level.upper()}] {message}")  # Log no console
    if level == 'debug':
        logging.debug(message)
    elif level == 'warning':
        logging.warning(message)
    elif level == 'error':
        logging.error(message)
    else:
        logging.info(message)

def execute_command(command):
    """Executa um comando no sistema operacional."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        log_message(f"Comando executado: {command}")
        return result.stdout, result.stderr
    except Exception as e:
        log_message(f"Erro ao executar comando: {e}", 'error')
        return None, str(e)

def open_application(app_name):
    """Abre uma aplicação no PC com tolerância fuzzy."""
    apps = load_apps()
    if not apps:
        log_message("Nenhum aplicativo cadastrado.", 'warning')
        return False

    # Buscar com tolerância alta (similaridade > 0.6)
    best_match = None
    best_ratio = 0
    for name, path in apps.items():
        ratio = difflib.SequenceMatcher(None, app_name.lower(), name.lower()).ratio()
        if ratio > best_ratio and ratio > 0.6:  # Tolerância alta
            best_match = path
            best_ratio = ratio

    if best_match:
        try:
            if os.name == 'nt':  # Windows
                os.startfile(best_match)
            else:
                subprocess.run(['open', best_match])  # macOS
            log_message(f"Aplicação aberta: {best_match} (correspondência: {best_ratio:.2f})")
            return True
        except Exception as e:
            log_message(f"Erro ao abrir aplicação: {e}", 'error')
            return False
    else:
        log_message(f"Aplicação não encontrada: {app_name}", 'warning')
        return False

def add_application(name, path):
    """Adiciona um novo aplicativo."""
    apps = load_apps()
    apps[name.lower()] = path
    save_apps(apps)
    log_message(f"Aplicativo adicionado: {name} -> {path}")

def load_apps():
    """Carrega aplicativos do arquivo."""
    try:
        with open('data/apps.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        log_message(f"Erro ao carregar apps: {e}", 'error')
        return {}

def save_apps(apps):
    """Salva aplicativos no arquivo."""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/apps.json', 'w', encoding='utf-8') as f:
            json.dump(apps, f, indent=4)
        log_message("Apps salvos com sucesso.")
    except Exception as e:
        log_message(f"Erro ao salvar apps: {e}", 'error')

def save_data_to_file(data, filename):
    """Salva dados em um arquivo."""
    try:
        with open(filename, 'w') as f:
            f.write(data)
        log_message(f"Dados salvos em: {filename}")
    except Exception as e:
        log_message(f"Erro ao salvar dados: {e}", 'error')
