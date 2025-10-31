import cv2
import numpy as np
import pyautogui
from PIL import Image
import time
import dxcam
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
try:
    from .config import SCREEN_CAPTURE_INTERVAL
    from .utils import log_message
except ImportError:
    from config import SCREEN_CAPTURE_INTERVAL
    from utils import log_message

class VisionModule:
    def __init__(self):
        self.screen_size = pyautogui.size()
        log_message(f"Tamanho da tela: {self.screen_size}")
        # Inicializar dxcam para captura de tela otimizada para ML/DL
        try:
            self.camera = dxcam.create(output_idx=0, output_color="BGR")
            self.camera.start(target_fps=60, video_mode=True)
            log_message("dxcam inicializado com sucesso para captura otimizada")
        except Exception as e:
            log_message(f"Erro ao inicializar dxcam: {e}, usando pyautogui como fallback", 'warning')
            self.camera = None

    def capture_screen(self, monitor=None):
        """Captura uma screenshot da tela usando dxcam otimizado para ML/DL."""
        try:
            # Usar dxcam se disponível (mais rápido para ML/DL)
            if self.camera is not None:
                frame = self.camera.get_latest_frame()
                if frame is not None:
                    return frame
                else:
                    log_message("dxcam não retornou frame, usando pyautogui", 'warning')
            else:
                log_message("dxcam não disponível, usando pyautogui", 'info')

            # Fallback direto para pyautogui
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
        except Exception as e:
            log_message(f"Erro na captura: {e}", 'error')
            # Retornar array vazio em caso de erro total
            return np.array([])

    def extract_text_from_screen(self, frame=None):
        """Extrai texto da tela usando OCR com múltiplas estratégias de teste."""
        try:
            if frame is None:
                frame = self.capture_screen()
            if frame.size == 0:
                return ""

            # Salvar imagem original para debug
            cv2.imwrite('debug_original.png', frame)

            # Estratégia 1: OCR direto na imagem original (sem pré-processamento)
            # log_message("=== TESTANDO ESTRATÉGIAS DE OCR ===")  # Removido para não poluir logs
            raw_text = pytesseract.image_to_string(frame, lang='por+eng')
            # log_message(f"OCR direto (sem processamento): '{raw_text[:100]}...'")  # Removido

            # Estratégia 2: Resize para 2x (pode melhorar reconhecimento)
            height, width = frame.shape[:2]
            resized = cv2.resize(frame, (width*2, height*2), interpolation=cv2.INTER_CUBIC)
            resized_text = pytesseract.image_to_string(resized, lang='por+eng')
            # log_message(f"OCR com resize 2x: '{resized_text[:100]}...'")  # Removido

            # Estratégia 3: Grayscale + CLAHE + threshold adaptativo
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cv2.imwrite('debug_gray.png', gray)

            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            cv2.imwrite('debug_enhanced.png', enhanced)

            thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
            cv2.imwrite('debug_thresh.png', thresh)

            # Testar diferentes PSM modes
            psm_configs = [
                ('--oem 3 --psm 3', 'PSM 3 - Fully automatic'),
                ('--oem 3 --psm 6', 'PSM 6 - Uniform block of text'),
                ('--oem 3 --psm 8', 'PSM 8 - Single word'),
                ('--oem 3 --psm 11', 'PSM 11 - Sparse text'),
                ('--oem 3 --psm 12', 'PSM 12 - Sparse text with OSD'),
            ]

            best_text = ""
            best_confidence = 0

            for config, description in psm_configs:
                try:
                    text = pytesseract.image_to_string(thresh, lang='por+eng', config=config)
                    # Tentar estimar confiança (número de caracteres não vazios)
                    confidence = len(text.strip())
                    log_message(f"{description}: '{text[:80]}...' (confiança: {confidence})")

                    if confidence > best_confidence:
                        best_text = text
                        best_confidence = confidence
                except Exception as e:
                    log_message(f"Erro com {description}: {e}")

            # Estratégia 4: Sem whitelist (permitir todos caracteres)
            try:
                no_whitelist_text = pytesseract.image_to_string(thresh, lang='por+eng', config='--oem 3 --psm 6')
                log_message(f"OCR sem whitelist: '{no_whitelist_text[:100]}...'")
                if len(no_whitelist_text.strip()) > best_confidence:
                    best_text = no_whitelist_text
            except Exception as e:
                log_message(f"Erro sem whitelist: {e}")

            # Limpar e normalizar texto final
            cleaned_text = best_text.strip()
            if cleaned_text:
                # Remover linhas vazias múltiplas e caracteres estranhos
                lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
                cleaned_text = '\n'.join(lines)
                # Remover caracteres não imprimíveis
                cleaned_text = ''.join(c for c in cleaned_text if c.isprintable())

            log_message(f"Texto final selecionado: '{cleaned_text[:100]}...'")
            return cleaned_text
        except Exception as e:
            log_message(f"Erro no OCR: {e}", 'error')
            return ""

    def save_video_frame(self, frame, filename):
        """Salva um frame como imagem para análise posterior."""
        try:
            success = cv2.imwrite(filename, frame)
            if success:
                log_message(f"Frame salvo: {filename}")
            return success
        except Exception as e:
            log_message(f"Erro ao salvar frame: {e}", 'error')
            return False

    def start_video_recording(self, filename, fps=30):
        """Inicia gravação de vídeo usando OpenCV VideoWriter."""
        try:
            if self.camera is not None:
                frame = self.camera.get_latest_frame()
                if frame is not None:
                    height, width = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    self.video_writer = cv2.VideoWriter(filename, fourcc, fps, (width, height))
                    self.is_recording = True
                    log_message(f"Gravação de vídeo iniciada: {filename}")
                    return True
            return False
        except Exception as e:
            log_message(f"Erro ao iniciar gravação: {e}", 'error')
            return False

    def record_frame(self, frame):
        """Grava um frame no vídeo se estiver gravando."""
        if self.is_recording and hasattr(self, 'video_writer'):
            try:
                self.video_writer.write(frame)
            except Exception as e:
                log_message(f"Erro ao gravar frame: {e}", 'error')

    def stop_video_recording(self):
        """Para a gravação de vídeo."""
        if self.is_recording and hasattr(self, 'video_writer'):
            try:
                self.video_writer.release()
                self.is_recording = False
                log_message("Gravação de vídeo parada.")
            except Exception as e:
                log_message(f"Erro ao parar gravação: {e}", 'error')

    def detect_objects(self, frame):
        """Placeholder para detecção de objetos (futuro: usar PyTorch ou TensorFlow)."""
        # Por enquanto, apenas detectar bordas simples com Canny
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            log_message(f"Detectados {len(contours)} objetos potenciais.")
            return len(contours)
        except Exception as e:
            log_message(f"Erro na detecção de objetos: {e}", 'error')
            return 0

    def generate_screen_report(self, text_data, object_count, duration):
        """Gera um relatório da atividade da tela."""
        report = f"Relatório de Atividade da Tela:\n"
        report += f"Duração: {duration} segundos\n"
        report += f"Texto detectado: {text_data[:500]}...\n" if text_data else "Nenhum texto detectado.\n"
        report += f"Objetos detectados: {object_count}\n"
        return report

    def get_all_monitors_context(self):
        """Captura contexto de todos os monitores disponíveis."""
        contexts = []

        # Usar pyautogui diretamente para evitar problemas de thread com mss
        try:
            screenshot = pyautogui.screenshot()
            width, height = screenshot.size
            contexts.append(f"Monitor principal: {width}x{height} pixels")

            # Tentar detectar múltiplos monitores via pyautogui
            try:
                import screeninfo
                monitors = screeninfo.get_monitors()
                if len(monitors) > 1:
                    for i, monitor in enumerate(monitors):
                        contexts.append(f"Monitor {i+1}: {monitor.width}x{monitor.height} pixels em ({monitor.x}, {monitor.y})")
                else:
                    contexts.append("Apenas um monitor detectado")
            except ImportError:
                log_message("screeninfo não instalado, usando detecção básica", 'info')
                contexts.append("Detecção de múltiplos monitores limitada")
            except Exception as e:
                log_message(f"Erro ao detectar monitores: {e}", 'warning')
                contexts.append("Erro na detecção de monitores")

        except Exception as e:
            log_message(f"Erro geral na captura: {e}", 'error')
            contexts.append("Monitor: Indisponível")

        return " | ".join(contexts)

    def get_screen_context(self):
        """Retorna o contexto visual atual da tela como descrição."""
        try:
            # Tentar capturar todos os monitores
            all_context = self.get_all_monitors_context()
            context = f"Telas disponíveis: {all_context}. Captura realizada."
        except Exception as e:
            # Fallback para captura simples
            log_message(f"Erro na captura multi-monitor: {e}, usando fallback", 'warning')
            if self.camera is not None:
                frame = self.camera.get_latest_frame()
                if frame is not None:
                    height, width = frame.shape[:2]
                    context = f"Tela capturada com dxcam: {width}x{height} pixels. 60 FPS ativo."
                else:
                    context = "Captura dxcam falhou, tela indisponível."
            else:
                context = "Sistema de captura não disponível."

        # Não logar constantemente para não poluir o console
        return context

    def continuous_monitoring(self, callback):
        """Monitora a tela continuamente com controle de memória e taxa."""
        log_message("Iniciando monitoramento contínuo...")
        frame_count = 0
        last_capture_time = time.time()

        while True:
            try:
                current_time = time.time()

                # Controlar taxa de captura (máximo 10 FPS para evitar sobrecarga)
                if current_time - last_capture_time < 0.1:  # 100ms mínimo entre capturas
                    time.sleep(0.05)  # Pequena pausa
                    continue

                # Usar dxcam se disponível
                if self.camera is not None:
                    frame = self.camera.get_latest_frame()
                    if frame is not None:
                        height, width = frame.shape[:2]
                        context = f"Tela capturada com dxcam: {width}x{height} pixels."

                        # Processar OCR a cada 60 frames (~1 FPS para análise pesada)
                        frame_count += 1
                        if frame_count % 60 == 0:
                            text = self.extract_text_from_screen(frame)
                            if text:
                                context += f" Texto detectado: {text[:100]}..."
                        else:
                            context += " Monitoramento ativo."
                    else:
                        context = "Captura temporariamente indisponível."
                else:
                    context = self.get_screen_context()

                callback(context)
                last_capture_time = current_time

                # Pausa controlada para não sobrecarregar CPU/GPU
                time.sleep(SCREEN_CAPTURE_INTERVAL)

            except Exception as e:
                log_message(f"Erro no monitoramento contínuo: {e}", 'error')
                time.sleep(1)  # Pausa maior em caso de erro
                # Tentar reinicializar câmera se necessário
                if "memória" in str(e).lower() or "COMError" in str(e):
                    log_message("Erro de memória detectado, tentando reinicializar câmera...")
                    try:
                        if self.camera:
                            self.camera.stop()
                            time.sleep(0.5)
                            self.camera.start(target_fps=30, video_mode=True)  # Reduzir FPS
                            log_message("Câmera reinicializada com 30 FPS")
                    except Exception as reinit_error:
                        log_message(f"Falha ao reinicializar câmera: {reinit_error}", 'error')
