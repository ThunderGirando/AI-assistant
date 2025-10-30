import time
import threading
import cv2
import numpy as np
import os
from action_recorder import ActionRecorder
from action_player import ActionPlayer
from vision import VisionModule
from config import DATA_PATH
from utils import log_message

class GamingAI:
    def __init__(self):
        self.recorder = ActionRecorder()
        self.player = ActionPlayer()
        self.vision = VisionModule()
        self.is_learning = False
        self.is_playing = False
        self.capture_thread = None

    def start_learning_session(self, session_name="learn_session"):
        """Inicia sessão de aprendizado observando o jogador humano."""
        if self.is_learning:
            log_message("Sessão de aprendizado já ativa.", 'warning')
            return

        log_message("Iniciando sessão de aprendizado...")
        self.recorder.start_recording(session_name)
        self.is_learning = True

        # Thread para capturar telas periodicamente (não todas as ações para não sobrecarregar)
        def capture_screens():
            frame_count = 0
            while self.is_learning:
                if self.recorder.recording and len(self.recorder.actions) > 0:
                    # Capturar tela a cada 10 ações para balancear performance
                    if len(self.recorder.actions) % 10 == 0:
                        frame = self.recorder.capture_screenshot()
                        if frame is not None:
                            # Salvar screenshot
                            filename = f"{DATA_PATH}gaming_sessions/{session_name}_frame_{frame_count}.png"
                            cv2.imwrite(filename, frame)
                            frame_count += 1
                time.sleep(0.5)  # Captura a cada 0.5s para não sobrecarregar

        self.capture_thread = threading.Thread(target=capture_screens, daemon=True)
        self.capture_thread.start()

    def stop_learning_session(self):
        """Para sessão de aprendizado."""
        if not self.is_learning:
            log_message("Nenhuma sessão de aprendizado ativa.", 'warning')
            return

        self.is_learning = False
        self.recorder.stop_recording()

        if self.capture_thread:
            self.capture_thread.join(timeout=2)

        log_message("Sessão de aprendizado finalizada.")

    def start_autonomous_playing(self, session_name, speed_multiplier=1.0):
        """Inicia jogo autônomo reproduzindo ações gravadas."""
        if self.is_playing:
            log_message("Já está jogando autônomo.", 'warning')
            return

        if not self.player.load_session(session_name):
            log_message("Erro ao carregar sessão para reprodução.", 'error')
            return

        self.is_playing = True
        log_message("Iniciando jogo autônomo...")

        # Thread para reprodução
        def play_actions():
            self.player.start_playback(speed_multiplier)
            self.is_playing = False

        play_thread = threading.Thread(target=play_actions, daemon=True)
        play_thread.start()

    def stop_autonomous_playing(self):
        """Para jogo autônomo."""
        if not self.is_playing:
            log_message("Nenhum jogo autônomo ativo.", 'warning')
            return

        self.player.stop_playback()
        self.is_playing = False
        log_message("Jogo autônomo parado.")

    def get_status(self):
        """Retorna status do Gaming AI."""
        return {
            'is_learning': self.is_learning,
            'is_playing': self.is_playing,
            'actions_recorded': len(self.recorder.actions) if self.recorder.recording else 0,
            'actions_loaded': len(self.player.actions)
        }

    def list_sessions(self):
        """Lista sessões gravadas disponíveis."""
        sessions_dir = f"{DATA_PATH}gaming_sessions"
        if not os.path.exists(sessions_dir):
            return []

        sessions = []
        for file in os.listdir(sessions_dir):
            if file.endswith('.csv'):
                sessions.append(file.replace('.csv', ''))

        return sessions

    def delete_session(self, session_name):
        """Deleta uma sessão gravada."""
        csv_file = f"{DATA_PATH}gaming_sessions/{session_name}.csv"
        png_files = [f for f in os.listdir(f"{DATA_PATH}gaming_sessions") if f.startswith(f"{session_name}_frame_")]

        deleted = 0
        try:
            if os.path.exists(csv_file):
                os.remove(csv_file)
                deleted += 1

            for png in png_files:
                os.remove(f"{DATA_PATH}gaming_sessions/{png}")
                deleted += 1

            log_message(f"Sessão {session_name} deletada: {deleted} arquivos removidos.")
            return True
        except Exception as e:
            log_message(f"Erro ao deletar sessão: {e}", 'error')
            return False
