import time
import pandas as pd
import numpy as np
import cv2
import os
from pynput import keyboard, mouse
from vision import VisionModule
from config import DATA_PATH
from utils import log_message

class ActionRecorder:
    def __init__(self):
        self.recording = False
        self.actions = []
        self.start_time = None
        self.vision = VisionModule()
        self.session_name = None

        # Listeners para mouse e teclado
        self.mouse_listener = None
        self.keyboard_listener = None

    def start_recording(self, session_name="gaming_session"):
        """Inicia gravação de sessão de jogo."""
        if self.recording:
            log_message("Já está gravando uma sessão.", 'warning')
            return

        self.recording = True
        self.actions = []
        self.start_time = time.time()
        self.session_name = session_name

        # Criar diretório se não existir
        os.makedirs(f"{DATA_PATH}gaming_sessions", exist_ok=True)

        # Inicializar listeners
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        log_message(f"Gravação iniciada: {session_name}")

    def stop_recording(self):
        """Para gravação e salva dados."""
        if not self.recording:
            log_message("Nenhuma gravação ativa.", 'warning')
            return

        self.recording = False

        # Parar listeners
        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        # Salvar dados
        self.save_session()
        log_message(f"Gravação parada. {len(self.actions)} ações capturadas.")

    def on_mouse_move(self, x, y):
        """Captura movimento do mouse."""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'timestamp': timestamp,
                'type': 'mouse_move',
                'x': x,
                'y': y,
                'button': None,
                'pressed': None,
                'key': None
            })

    def on_mouse_click(self, x, y, button, pressed):
        """Captura cliques do mouse."""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'timestamp': timestamp,
                'type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
                'key': None
            })

    def on_key_press(self, key):
        """Captura pressionamento de tecla."""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'timestamp': timestamp,
                'type': 'key_press',
                'x': None,
                'y': None,
                'button': None,
                'pressed': None,
                'key': str(key)
            })

    def on_key_release(self, key):
        """Captura liberação de tecla."""
        if self.recording:
            timestamp = time.time() - self.start_time
            self.actions.append({
                'timestamp': timestamp,
                'type': 'key_release',
                'x': None,
                'y': None,
                'button': None,
                'pressed': None,
                'key': str(key)
            })

    def capture_screenshot(self):
        """Captura screenshot atual e retorna."""
        frame = self.vision.capture_screen()
        return frame

    def save_session(self):
        """Salva sessão em CSV."""
        if self.actions:
            df = pd.DataFrame(self.actions)
            filename = f"{DATA_PATH}gaming_sessions/{self.session_name}.csv"
            df.to_csv(filename, index=False)
            log_message(f"Sessão salva: {filename} com {len(self.actions)} ações")
        else:
            log_message("Nenhuma ação para salvar.", 'warning')
