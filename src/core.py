import threading
import time
import asyncio
import cv2
import pytesseract
from concurrent.futures import ThreadPoolExecutor
try:
    from voice import VoiceAssistant
    from vision import VisionModule
    from ai_api import AIAPI
    from voice_recognition import VoiceRecognition
    from learning_mode import LearningMode
    from utils import setup_logging, log_message
    from config import WAKE_WORD
    from commands import open_apps, manage_apps, vision_commands, learning_commands
except ImportError:
    from .voice import VoiceAssistant
    from .vision import VisionModule
    from .ai_api import AIAPI
    from .voice_recognition import VoiceRecognition
    from .learning_mode import LearningMode
    from .utils import setup_logging, log_message
    from .config import WAKE_WORD
    from commands import open_apps, manage_apps, vision_commands, learning_commands

class StarkCore:
    def __init__(self):
        setup_logging()
        self.voice = VoiceAssistant()
        self.vision = VisionModule()
        self.ai = AIAPI()
        self.voice_recog = VoiceRecognition()
        self.learning_mode = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.vision_cache = {"last_text": "", "last_frame_hash": None}

    def optimize_ocr(self, frame):
        """OCR otimizado com cache e comparação de frames."""
        try:
            frame_hash = hash(frame.tobytes())
            if frame_hash == self.vision_cache["last_frame_hash"]:
                return self.vision_cache["last_text"]

            # Pré-processamento melhorado
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Aumentar contraste com CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)

            # Threshold adaptativo mais agressivo
            thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            # Dilatação para conectar caracteres
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))
            dilated = cv2.dilate(thresh, kernel, iterations=1)

            # Tentar PSM 3 (automático) primeiro
            text = pytesseract.image_to_string(dilated, lang='por+eng', config='--oem 3 --psm 3')

            # Se PSM 3 falhar, tentar PSM 6
            if not text.strip():
                text = pytesseract.image_to_string(dilated, lang='por+eng', config='--oem 3 --psm 6')

            cleaned = text.strip()
            if cleaned:
                # Filtrar linhas muito curtas ou com muitos símbolos
                lines = []
                for line in cleaned.split('\n'):
                    line = line.strip()
                    if len(line) > 3 and sum(1 for c in line if c.isalpha() or c.isspace()) / len(line) > 0.5:
                        lines.append(line)
                cleaned = '\n'.join(lines)
                cleaned = ''.join(c for c in cleaned if c.isprintable() or c in 'ãõçáéíóúâêôàèìòù')

            self.vision_cache["last_text"] = cleaned
            self.vision_cache["last_frame_hash"] = frame_hash
            return cleaned
        except Exception as e:
            log_message(f"Erro OCR otimizado: {e}")
            return ""

    def handle_command_async(self, command):
        """Processa comando de forma assíncrona."""
        def _process():
            try:
                context = self.vision.get_screen_context()
                if self._try_local_commands(command, context):
                    return
                self._fallback_to_gemini(command, context)
            except Exception as e:
                log_message(f"Erro processando comando: {e}")
                self.voice.speak("Erro interno. Tente novamente.")

        self.executor.submit(_process)

    def _try_local_commands(self, command, context):
        """Tenta comandos locais organizados."""
        if open_apps.handle_open_command(command, self.voice):
            return True
        if manage_apps.handle_add_app_command(command, self.voice):
            return True
        if manage_apps.handle_list_apps_command(command, self.voice):
            return True
        if vision_commands.handle_vision_command(command, self.voice, self.vision, self.learning_mode, LearningMode, self.ai):
            return True
        if learning_commands.handle_learning_command(command, self.voice, self.vision, self.ai, self.learning_mode, LearningMode):
            return True

        if 'gravar voz' in command or 'treinar voz' in command:
            self._handle_voice_training()
            return True

        if 'sair' in command or 'parar' in command:
            self.voice.speak("Até logo!")
            return False

        return False

    def _handle_voice_training(self):
        self.voice.speak("Vou gravar algumas amostras da sua voz. Diga 'pronto' quando estiver pronto.")
        ready = self.voice.listen()
        if ready and 'pronto' in ready:
            self.voice.speak("Gravando primeira amostra... diga 'STARK'.")
            self.voice_recog.record_voice_sample('user')
            self.voice.speak("Segunda amostra... diga 'STARK' novamente.")
            self.voice_recog.record_voice_sample('user')
            self.voice.speak("Terceira amostra... diga 'STARK' mais uma vez.")
            self.voice_recog.record_voice_sample('user')
            self.voice.speak("Treinando modelo...")
            if self.voice_recog.train_voice_model('user'):
                self.voice.speak("Modelo treinado!")
            else:
                self.voice.speak("Falha no treinamento.")

    def _fallback_to_gemini(self, command, context):
        """Fallback inteligente com Gemini."""
        prompt = f"Usuário disse: '{command}'. Contexto: {context[:200]}. Interprete como comando para IA assistente. Se for abrir app, OCR, jogo ou tarefa, diga claramente. Se ambíguo, pergunte o que fazer."
        response = self.ai.generate_response(prompt, context)
        self.voice.speak(response)

    def _handle_learning_response(self, response):
        """Processa resposta de aprendizado."""
        if self.learning_mode and self.learning_mode.process_learning_response(response):
            self.voice.speak("Obrigado!")
            return True
        return False

    def start_voice_loop(self):
        """Loop de voz em thread separada."""
        def voice_worker():
            while True:
                try:
                    if self.learning_mode and self.learning_mode.questions_queue:
                        unanswered = [q for q in self.learning_mode.questions_queue if not q['answered']]
                        if unanswered:
                            self.voice.speak("Estou ouvindo sua resposta...")
                            response = self.voice.listen(timeout=10)
                            if response and self._handle_learning_response(response):
                                continue
                            else:
                                self.voice.speak("Não entendi.")
                                time.sleep(0.1)
                                continue

                    command = self.voice.listen_for_wake_word()
                    if command:
                        self.handle_command_async(command)
                        time.sleep(0.1)

                except Exception as e:
                    log_message(f"Erro no loop de voz: {e}")
                    time.sleep(1)

        threading.Thread(target=voice_worker, daemon=True).start()

    def start_vision_loop(self):
        """Loop de visão otimizado em thread separada."""
        def vision_worker():
            frame_count = 0
            last_time = time.time()
            while True:
                try:
                    current_time = time.time()
                    if current_time - last_time < 0.1:
                        time.sleep(0.05)
                        continue

                    if self.vision.camera:
                        frame = self.vision.camera.get_latest_frame()
                        if frame is not None:
                            frame_count += 1
                            if frame_count % 60 == 0:
                                text = self.optimize_ocr(frame)
                                log_message(f"OCR Frame {frame_count}: '{text}'")

                                # Salvar screenshot para debug
                                debug_path = f"debug_screenshot_{frame_count}.png"
                                cv2.imwrite(debug_path, frame)
                                log_message(f"Screenshot salvo: {debug_path}")

                    last_time = current_time
                    time.sleep(0.05)

                except Exception as e:
                    log_message(f"Erro no loop de visão: {e}")
                    time.sleep(1)

        threading.Thread(target=vision_worker, daemon=True).start()

    def run(self):
        """Inicia Stark AI com threads paralelas."""
        log_message("Stark AI iniciando...")
        self.voice.speak("Sistema STARK iniciado. Diga 'STARK' para me chamar.")

        self.start_vision_loop()
        self.start_voice_loop()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log_message("Stark AI finalizado.")
            self.executor.shutdown()
