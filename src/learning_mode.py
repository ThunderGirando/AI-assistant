import time
import threading
import winsound  # Para Windows, tocar som
import pyautogui
from utils import log_message
from config import DEBUG_MODE

class LearningMode:
    def __init__(self, voice_assistant, vision_module, ai_api):
        self.voice = voice_assistant
        self.vision = vision_module
        self.ai = ai_api
        self.is_learning = False
        self.observations = []
        self.questions_queue = []
        self.learning_thread = None
        self.specific_monitor = None  # None = todos os monitores, int = monitor específico

    def start_learning(self):
        """Inicia o modo de aprendizado."""
        if self.is_learning:
            log_message("Modo de aprendizado já está ativo.")
            return

        self.is_learning = True
        self.observations = []
        log_message("Modo de aprendizado iniciado. Observando a tela...")

        # Iniciar thread de aprendizado
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()

    def stop_learning(self):
        """Para o modo de aprendizado."""
        self.is_learning = False
        if self.learning_thread:
            self.learning_thread.join(timeout=1)
        log_message("Modo de aprendizado parado.")

    def _learning_loop(self):
        """Loop principal do aprendizado."""
        question_interval = 30    # Segundos entre perguntas

        last_question = time.time()

        while self.is_learning:
            current_time = time.time()

            # Fazer observação contínua - considerar monitor específico se definido
            if self.specific_monitor is not None:
                # Observar apenas o monitor específico usando screeninfo para coordenadas reais
                try:
                    import screeninfo
                    monitors = screeninfo.get_monitors()

                    if 1 <= self.specific_monitor <= len(monitors):
                        monitor = monitors[self.specific_monitor - 1]
                        # Capturar screenshot do monitor específico com coordenadas reais
                        screenshot = pyautogui.screenshot(region=(monitor.x, monitor.y, monitor.width, monitor.height))
                        height, width = screenshot.size
                        context = f"Monitor {self.specific_monitor}: {width}x{height} pixels em ({monitor.x}, {monitor.y}). Captura realizada."
                    else:
                        context = f"Monitor {self.specific_monitor} não encontrado. Usando contexto geral."
                        context = self.vision.get_screen_context()

                except ImportError:
                    log_message("screeninfo não disponível, usando captura geral", 'warning')
                    context = self.vision.get_screen_context()
                except Exception as e:
                    log_message(f"Erro ao observar monitor específico {self.specific_monitor}: {e}", 'warning')
                    context = self.vision.get_screen_context()
            else:
                # Observar todos os monitores
                context = self.vision.get_screen_context()

            if context:
                self.observations.append({
                    'timestamp': current_time,
                    'context': context,
                    'action': 'observing',
                    'monitor': self.specific_monitor
                })
                # Não logar observações constantes para não poluir o console

            # Fazer pergunta periódica
            if current_time - last_question >= question_interval:
                self._ask_learning_question()
                last_question = current_time

            time.sleep(2)  # Pausa maior para não sobrecarregar com observações contínuas

    def _ask_learning_question(self):
        """Faz uma pergunta de aprendizado."""
        if not self.observations:
            question = "O que você está fazendo agora na tela?"
        else:
            # Gerar pergunta baseada nas observações recentes
            recent_obs = self.observations[-3:] if len(self.observations) >= 3 else self.observations
            contexts = [obs['context'] for obs in recent_obs]
            question = self.ai.generate_learning_question(contexts)

        # Tocar som de notificação
        self._play_notification_sound()

        # Falar a pergunta diretamente (sem mostrar no terminal)
        self.voice.speak(f"Pergunta de aprendizado: {question}")

        # Adicionar à fila de perguntas
        self.questions_queue.append({
            'question': question,
            'timestamp': time.time(),
            'answered': False
        })

    def _play_notification_sound(self):
        """Toca um som de notificação."""
        try:
            # Som de notificação do Windows (asterisco)
            winsound.MessageBeep(winsound.SND_ALIAS)
        except Exception as e:
            log_message(f"Erro ao tocar som: {e}", 'warning')

    def process_learning_response(self, response):
        """Processa uma resposta de aprendizado."""
        if not self.questions_queue:
            return False

        # Pegar a última pergunta não respondida
        unanswered = [q for q in self.questions_queue if not q['answered']]
        if not unanswered:
            return False

        last_question = unanswered[-1]
        last_question['answered'] = True
        last_question['response'] = response
        last_question['response_timestamp'] = time.time()

        # Adicionar à observações
        self.observations.append({
            'timestamp': time.time(),
            'context': f"Pergunta: {last_question['question']} | Resposta: {response}",
            'action': 'learning_response'
        })

        log_message(f"Resposta de aprendizado registrada: {response}")

        # Usar IA para aprender com a resposta
        self.ai.learn_from_response(last_question['question'], response, self.observations)

        return True

    def get_learning_status(self):
        """Retorna status do aprendizado."""
        return {
            'is_learning': self.is_learning,
            'observations_count': len(self.observations),
            'unanswered_questions': len([q for q in self.questions_queue if not q['answered']])
        }
