import os
import subprocess
import logging
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
    """Abre uma aplicação no PC."""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(app_name)
        else:
            subprocess.run(['open', app_name])
        log_message(f"Aplicação aberta: {app_name}")
    except Exception as e:
        log_message(f"Erro ao abrir aplicação: {e}", 'error')

def save_data_to_file(data, filename):
    """Salva dados em um arquivo."""
    try:
        with open(filename, 'w') as f:
            f.write(data)
        log_message(f"Dados salvos em: {filename}")
    except Exception as e:
        log_message(f"Erro ao salvar dados: {e}", 'error')
