import cv2
import numpy as np
import pyautogui
from PIL import Image
import time
from config import SCREEN_CAPTURE_INTERVAL
from utils import log_message

class VisionModule:
    def __init__(self):
        self.screen_size = pyautogui.size()
        log_message(f"Tamanho da tela: {self.screen_size}")

    def capture_screen(self):
        """Captura uma screenshot da tela."""
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def get_screen_context(self):
        """Retorna o contexto visual atual da tela como descrição."""
        frame = self.capture_screen()
        # Por enquanto, apenas retorna informações básicas
        # Futuramente, pode usar OCR ou visão computacional para descrever o que está na tela
        height, width = frame.shape[:2]
        context = f"Tela de {width}x{height} pixels. Captura realizada."
        # Não logar constantemente para não poluir o console
        return context

    def continuous_monitoring(self, callback):
        """Monitora a tela continuamente e chama callback com contexto."""
        # Não logar o início para não poluir
        while True:
            context = self.get_screen_context()
            callback(context)
            time.sleep(SCREEN_CAPTURE_INTERVAL)
