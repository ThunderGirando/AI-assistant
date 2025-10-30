import os
import subprocess
import logging
import json
import difflib
try:
    from .config import LOG_FILE, DEBUG_MODE
except ImportError:
    from config import LOG_FILE, DEBUG_MODE

def setup_logging():
    """Configura logging com rotação de arquivos."""
    # Verificar se já existem logs antigos
    log_files = [f for f in os.listdir('.') if f.startswith(LOG_FILE.replace('.log', '')) and f.endswith('.log')]
    log_files.sort(reverse=True)  # Mais recentes primeiro

    # Manter apenas 2 logs
    while len(log_files) > 2:
        os.remove(log_files.pop())

    # Renomear logs existentes
    for i, log_file in enumerate(log_files):
        if i == 0:
            os.rename(log_file, f"{LOG_FILE.replace('.log', '')}_2.log")
        elif i == 1:
            os.rename(log_file, f"{LOG_FILE.replace('.log', '')}_1.log")

    # Configurar logging no arquivo principal
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
    """Abre uma aplicação no PC com tolerância fuzzy e atualização automática de caminhos."""
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
        # Verificar se o caminho ainda existe, se não, tentar atualizar
        if not os.path.exists(best_match):
            log_message(f"Caminho desatualizado para {app_name}: {best_match}", 'warning')
            updated_path = update_app_path(app_name, best_match)
            if updated_path:
                best_match = updated_path
                log_message(f"Caminho atualizado para {app_name}: {best_match}")
            else:
                log_message(f"Não foi possível atualizar o caminho para {app_name}", 'error')
                return False

        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen([best_match], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.run(['open', best_match], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # macOS
            log_message(f"Aplicação aberta: {best_match} (correspondência: {best_ratio:.2f})")
            return True
        except Exception as e:
            log_message(f"Erro ao abrir aplicação: {e}", 'error')
            return False
    else:
        log_message(f"Aplicação não encontrada: {app_name}", 'warning')
        return False

def update_app_path(app_name, old_path):
    """Atualiza o caminho de um aplicativo procurando na pasta base."""
    try:
        # Extrair pasta base do caminho antigo (subir dois níveis para chegar à pasta do app)
        base_dir = os.path.dirname(os.path.dirname(old_path))  # Ex.: C:\Users\guilh\AppData\Local\Discord
        app_dir = os.path.basename(base_dir)  # ex.: Discord

        # Procurar por pastas de versão (app-X.X.XXXX)
        if os.path.exists(base_dir):
            subdirs = [d for d in os.listdir(base_dir) if d.startswith('app-') and os.path.isdir(os.path.join(base_dir, d))]
            if subdirs:
                # Pegar a pasta mais recente (ordenar por nome, assumindo versão no nome)
                subdirs.sort(reverse=True)
                latest_dir = os.path.join(base_dir, subdirs[0])
                exe_path = os.path.join(latest_dir, f"{app_dir}.exe")
                if os.path.exists(exe_path):
                    # Atualizar no JSON
                    apps = load_apps()
                    apps[app_name.lower()] = exe_path
                    save_apps(apps)
                    return exe_path
    except Exception as e:
        log_message(f"Erro ao atualizar caminho de {app_name}: {e}", 'error')
    return None

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

def match_command(command, keywords, threshold=0.8):
    """Verifica se o comando contém palavras-chave similares."""
    words = command.lower().split()
    for word in words:
        for keyword in keywords:
            ratio = difflib.SequenceMatcher(None, word, keyword.lower()).ratio()
            if ratio > threshold:
                return True, word  # Retorna True e a palavra encontrada
    return False, None

def extract_app_name(command, command_word):
    """Extrai o nome do aplicativo do comando."""
    # Remove a palavra de comando e palavras comuns
    words = command.lower().split()
    try:
        idx = words.index(command_word.lower())
        app_words = words[idx + 1:]  # Palavras após o comando
        # Remove palavras de preenchimento como "o", "a", "por favor", etc.
        fillers = ['o', 'a', 'por', 'favor', 'ai', 'porfavor', 'me']
        app_words = [w for w in app_words if w not in fillers]
        return ' '.join(app_words).strip()
    except ValueError:
        return command.replace(command_word, '').strip()

def save_data_to_file(data, filename):
    """Salva dados em um arquivo."""
    try:
        with open(filename, 'w') as f:
            f.write(data)
        log_message(f"Dados salvos em: {filename}")
    except Exception as e:
        log_message(f"Erro ao salvar dados: {e}", 'error')
