import time
import pyautogui
import pydirectinput
from config import DATA_PATH
from utils import log_message

class ActionPlayer:
    def __init__(self):
        self.playing = False
        self.actions = []
        self.current_index = 0
        self.start_time = None

    def load_session(self, session_name):
        """Carrega sessão gravada."""
        import pandas as pd
        filename = f"{DATA_PATH}gaming_sessions/{session_name}.csv"
        try:
            df = pd.read_csv(filename)
            self.actions = df.to_dict('records')
            log_message(f"Sessão carregada: {len(self.actions)} ações")
            return True
        except Exception as e:
            log_message(f"Erro ao carregar sessão: {e}", 'error')
            return False

    def start_playback(self, speed_multiplier=1.0):
        """Inicia reprodução das ações."""
        if not self.actions:
            log_message("Nenhuma ação carregada.", 'warning')
            return

        self.playing = True
        self.current_index = 0
        self.start_time = time.time()
        self.speed_multiplier = speed_multiplier

        log_message(f"Iniciando reprodução com velocidade {speed_multiplier}x")

        while self.playing and self.current_index < len(self.actions):
            action = self.actions[self.current_index]

            # Calcular tempo de espera baseado no timestamp
            if self.current_index > 0:
                prev_action = self.actions[self.current_index - 1]
                time_diff = (action['timestamp'] - prev_action['timestamp']) / speed_multiplier
                if time_diff > 0:
                    time.sleep(time_diff)

            # Executar ação
            self.execute_action(action)
            self.current_index += 1

        self.playing = False
        log_message("Reprodução finalizada.")

    def stop_playback(self):
        """Para reprodução."""
        self.playing = False
        log_message("Reprodução parada.")

    def execute_action(self, action):
        """Executa uma ação específica."""
        action_type = action['type']

        try:
            if action_type == 'mouse_move':
                pydirectinput.moveTo(int(action['x']), int(action['y']))

            elif action_type == 'mouse_click':
                if action['pressed']:
                    if 'left' in str(action['button']).lower():
                        pydirectinput.mouseDown(button='left')
                    elif 'right' in str(action['button']).lower():
                        pydirectinput.mouseDown(button='right')
                else:
                    if 'left' in str(action['button']).lower():
                        pydirectinput.mouseUp(button='left')
                    elif 'right' in str(action['button']).lower():
                        pydirectinput.mouseUp(button='right')

            elif action_type == 'key_press':
                key = self.normalize_key(action['key'])
                if key:
                    pydirectinput.keyDown(key)

            elif action_type == 'key_release':
                key = self.normalize_key(action['key'])
                if key:
                    pydirectinput.keyUp(key)

        except Exception as e:
            log_message(f"Erro ao executar ação {action_type}: {e}", 'error')

    def normalize_key(self, key_str):
        """Normaliza string de tecla para pydirectinput."""
        if not key_str:
            return None

        # Remover aspas e converter para minúsculo
        key = str(key_str).strip("'\"").lower()

        # Mapeamento de teclas especiais
        key_map = {
            'key.space': 'space',
            'key.enter': 'enter',
            'key.tab': 'tab',
            'key.backspace': 'backspace',
            'key.shift': 'shift',
            'key.ctrl': 'ctrl',
            'key.alt': 'alt',
            'key.esc': 'esc',
            'key.f1': 'f1',
            'key.f2': 'f2',
            'key.f3': 'f3',
            'key.f4': 'f4',
            'key.f5': 'f5',
            'key.f6': 'f6',
            'key.f7': 'f7',
            'key.f8': 'f8',
            'key.f9': 'f9',
            'key.f10': 'f10',
            'key.f11': 'f11',
            'key.f12': 'f12',
        }

        return key_map.get(key, key)
