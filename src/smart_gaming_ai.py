import time
import threading
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
import os
from action_recorder import ActionRecorder
from action_player import ActionPlayer
from vision import VisionModule
from config import DATA_PATH, GEMINI_API_KEY
from utils import log_message
import google.generativeai as genai

class SmartGamingAI:
    def __init__(self):
        self.recorder = ActionRecorder()
        self.player = ActionPlayer()
        self.vision = VisionModule()
        self.is_learning = False
        self.is_playing_smart = False
        self.model = None
        self.session_name = None

        # Configurar Gemini AI
        genai.configure(api_key=GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')

        # Carregar modelo se existir
        self.load_model()

    def create_model(self, input_shape=(224, 224, 3)):
        """Cria modelo de CNN para behavior cloning."""
        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            # Outputs: mouse_x, mouse_y, click_type, key_actions
            layers.Dense(6, activation='linear')  # Regressão para coordenadas e ações
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        return model

    def load_model(self):
        """Carrega modelo treinado se existir."""
        model_path = f"{DATA_PATH}gaming_models/smart_gaming_model.h5"
        if os.path.exists(model_path):
            try:
                self.model = tf.keras.models.load_model(model_path)
                log_message("Modelo de gaming inteligente carregado.")
            except Exception as e:
                log_message(f"Erro ao carregar modelo: {e}", 'error')
                self.model = self.create_model()
        else:
            self.model = self.create_model()
            log_message("Novo modelo de gaming criado.")

    def save_model(self):
        """Salva o modelo treinado."""
        os.makedirs(f"{DATA_PATH}gaming_models", exist_ok=True)
        model_path = f"{DATA_PATH}gaming_models/smart_gaming_model.h5"
        try:
            self.model.save(model_path)
            log_message("Modelo salvo com sucesso.")
        except Exception as e:
            log_message(f"Erro ao salvar modelo: {e}", 'error')

    def preprocess_screenshot(self, frame):
        """Pré-processa screenshot para entrada no modelo."""
        if frame is None:
            return None

        # Redimensionar para 224x224
        frame = cv2.resize(frame, (224, 224))
        # Normalizar para [0, 1]
        frame = frame.astype(np.float32) / 255.0
        return frame

    def start_learning_session(self, session_name="smart_learn_session"):
        """Inicia sessão de aprendizado inteligente."""
        if self.is_learning:
            log_message("Sessão de aprendizado já ativa.", 'warning')
            return

        log_message("Iniciando sessão de aprendizado inteligente...")
        self.recorder.start_recording(session_name)
        self.session_name = session_name
        self.is_learning = True

        # Thread para capturar e analisar telas
        def smart_learning():
            frame_count = 0
            while self.is_learning:
                if self.recorder.recording and len(self.recorder.actions) > 0:
                    # Capturar tela atual
                    frame = self.recorder.capture_screenshot()
                    if frame is not None:
                        processed_frame = self.preprocess_screenshot(frame)

                        # Analisar padrão de jogo usando Gemini se necessário
                        if frame_count % 50 == 0:  # A cada 50 frames, analisar contexto
                            analysis = self.analyze_game_context(frame)
                            log_message(f"Análise de contexto: {analysis}")

                        frame_count += 1
                time.sleep(0.2)  # Captura a cada 0.2s para análise mais frequente

        self.learning_thread = threading.Thread(target=smart_learning, daemon=True)
        self.learning_thread.start()

    def stop_learning_session(self):
        """Para sessão de aprendizado e treina modelo."""
        if not self.is_learning:
            log_message("Nenhuma sessão de aprendizado ativa.", 'warning')
            return

        self.is_learning = False
        self.recorder.stop_recording()

        if self.learning_thread:
            self.learning_thread.join(timeout=2)

        # Treinar modelo com dados capturados
        self.train_model()
        log_message("Sessão de aprendizado finalizada e modelo treinado.")

    def train_model(self):
        """Treina modelo com dados da sessão."""
        data_file = f"{DATA_PATH}gaming_sessions/{self.session_name}.csv"
        if not os.path.exists(data_file):
            log_message("Arquivo de dados não encontrado.", 'error')
            return

        try:
            df = pd.read_csv(data_file)
            log_message(f"Dados carregados: {len(df)} ações")

            # Preparar dados de treinamento
            X_frames = []
            y_actions = []

            # Para cada ação, carregar screenshot correspondente e preparar labels
            for idx, row in df.iterrows():
                # Tentar carregar screenshot (se existir)
                screenshot_path = f"{DATA_PATH}gaming_sessions/{self.session_name}_frame_{idx}.png"
                if os.path.exists(screenshot_path):
                    frame = cv2.imread(screenshot_path)
                    processed_frame = self.preprocess_screenshot(frame)

                    if processed_frame is not None:
                        X_frames.append(processed_frame)

                        # Preparar labels: [mouse_x, mouse_y, click_type, key_code, press/release]
                        action_vector = [
                            row.get('x', 0) / 1920,  # Normalizar coordenadas
                            row.get('y', 0) / 1080,
                            1 if row.get('type') == 'mouse_click' else 0,
                            hash(str(row.get('key', ''))) % 100 / 100,  # Hash simples para teclas
                            1 if row.get('pressed', False) else 0
                        ]
                        y_actions.append(action_vector)

            if X_frames and y_actions:
                X = np.array(X_frames)
                y = np.array(y_actions)

                # Treinar modelo
                history = self.model.fit(X, y, epochs=10, batch_size=32, validation_split=0.2)
                log_message(f"Modelo treinado. Loss final: {history.history['loss'][-1]:.4f}")

                # Salvar modelo
                self.save_model()
            else:
                log_message("Dados insuficientes para treinamento.", 'warning')

        except Exception as e:
            log_message(f"Erro no treinamento: {e}", 'error')

    def start_smart_playing(self, creativity_level=0.7):
        """Inicia jogo inteligente com criatividade."""
        if self.is_playing_smart:
            log_message("Já está jogando inteligente.", 'warning')
            return

        if self.model is None:
            log_message("Modelo não carregado.", 'error')
            return

        self.is_playing_smart = True
        self.creativity_level = creativity_level
        log_message(f"Iniciando jogo inteligente com criatividade {creativity_level}...")

        def smart_play():
            import pyautogui
            import pydirectinput

            while self.is_playing_smart:
                # Capturar tela atual
                frame = self.vision.capture_screen()
                if frame is not None:
                    processed_frame = self.preprocess_screenshot(frame)
                    if processed_frame is not None:
                        # Fazer batch para predição
                        X = np.expand_dims(processed_frame, axis=0)

                        # Prever ação
                        prediction = self.model.predict(X, verbose=0)[0]

                        # Decodificar predição com criatividade
                        mouse_x = int(prediction[0] * 1920)
                        mouse_y = int(prediction[1] * 1080)
                        should_click = prediction[2] > 0.5
                        key_hash = prediction[3]
                        should_press = prediction[4] > 0.5

                        # Aplicar criatividade (ruído aleatório)
                        if np.random.random() < self.creativity_level:
                            mouse_x += np.random.randint(-50, 50)
                            mouse_y += np.random.randint(-50, 50)
                            should_click = np.random.random() < 0.3  # 30% chance de clicar quando criativo

                        # Limitar coordenadas
                        mouse_x = np.clip(mouse_x, 0, 1920)
                        mouse_y = np.clip(mouse_y, 0, 1080)

                        # Executar ação
                        pydirectinput.moveTo(mouse_x, mouse_y)

                        if should_click:
                            pydirectinput.click()

                        # Simular timing humano
                        time.sleep(np.random.uniform(0.1, 0.5))

                time.sleep(0.3)  # Decisões a cada 0.3s

        self.play_thread = threading.Thread(target=smart_play, daemon=True)
        self.play_thread.start()

    def stop_smart_playing(self):
        """Para jogo inteligente."""
        if not self.is_playing_smart:
            log_message("Nenhum jogo inteligente ativo.", 'warning')
            return

        self.is_playing_smart = False
        if self.play_thread:
            self.play_thread.join(timeout=2)
        log_message("Jogo inteligente parado.")

    def analyze_game_context(self, frame):
        """Analisa contexto do jogo usando Gemini Vision."""
        try:
            # Converter frame para formato aceito pelo Gemini
            _, buffer = cv2.imencode('.jpg', frame)
            image_bytes = buffer.tobytes()

            # Criar prompt para análise
            prompt = """
            Analise esta captura de tela de jogo. Descreva:
            1. Que tipo de jogo parece ser?
            2. Qual é o estado atual do jogo?
            3. Que ações o jogador humano provavelmente faria agora?
            4. Há algum padrão ou estratégia visível?

            Seja conciso e foque em elementos de jogabilidade.
            """

            response = self.gemini_model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes}
            ])

            analysis = response.text.strip()
            return analysis

        except Exception as e:
            log_message(f"Erro na análise com Gemini: {e}", 'error')
            return "Análise não disponível"

    def ask_gemini_help(self, question, context_frame=None):
        """Pergunta ajuda ao Gemini sobre estratégias de jogo."""
        try:
            prompt = f"""
            Como IA assistente de gaming, ajude com esta pergunta sobre jogos/estratégias:

            Pergunta: {question}

            Forneça uma resposta útil e prática focada em estratégias de jogo.
            """

            if context_frame is not None:
                # Incluir imagem se disponível
                _, buffer = cv2.imencode('.jpg', context_frame)
                image_bytes = buffer.tobytes()

                response = self.gemini_model.generate_content([
                    prompt,
                    {"mime_type": "image/jpeg", "data": image_bytes}
                ])
            else:
                # Texto apenas
                response = self.gemini_model.generate_content(prompt)

            return response.text.strip()

        except Exception as e:
            log_message(f"Erro ao consultar Gemini: {e}", 'error')
            return "Desculpe, não consegui obter ajuda no momento."

    def get_status(self):
        """Retorna status da Gaming AI inteligente."""
        return {
            'is_learning': self.is_learning,
            'is_playing_smart': self.is_playing_smart,
            'creativity_level': getattr(self, 'creativity_level', 0),
            'model_loaded': self.model is not None,
            'session_name': self.session_name
        }
