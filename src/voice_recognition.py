import librosa
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from config import MODEL_SAVE_PATH, DATA_PATH
from utils import log_message

class VoiceRecognition:
    def __init__(self):
        self.model = None
        self.load_model()

    def extract_features(self, audio_path):
        """Extrai features MFCC do áudio."""
        try:
            y, sr = librosa.load(audio_path, sr=22050)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            return mfccs_mean
        except Exception as e:
            log_message(f"Erro ao extrair features: {e}", 'error')
            return None

    def record_voice_sample(self, name, duration=3):
        """Grava uma amostra de voz para treinamento."""
        import sounddevice as sd
        import scipy.io.wavfile as wav

        log_message(f"Gravando amostra de voz para '{name}' por {duration} segundos...")
        fs = 22050  # Sample rate
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()  # Wait until recording is finished

        # Criar diretório se não existir
        sample_dir = f"{DATA_PATH}voice_samples"
        os.makedirs(sample_dir, exist_ok=True)

        # Contar arquivos existentes
        existing_files = [f for f in os.listdir(sample_dir) if f.startswith(name) and f.endswith('.wav')]
        filename = f"{sample_dir}/{name}_{len(existing_files)}.wav"

        wav.write(filename, fs, recording)
        log_message(f"Amostra salva em: {filename}")
        return filename

    def train_voice_model(self, user_name):
        """Treina modelo de reconhecimento de voz do usuário."""
        samples_dir = f"{DATA_PATH}voice_samples/"
        if not os.path.exists(samples_dir):
            log_message("Nenhuma amostra de voz encontrada.", 'warning')
            return False

        features = []
        labels = []

        for file in os.listdir(samples_dir):
            if file.startswith(user_name) and file.endswith('.wav'):
                feature = self.extract_features(os.path.join(samples_dir, file))
                if feature is not None:
                    features.append(feature)
                    labels.append(1)  # 1 para voz do usuário

        # Adicionar amostras negativas (outras vozes)
        for file in os.listdir(samples_dir):
            if not file.startswith(user_name) and file.endswith('.wav'):
                feature = self.extract_features(os.path.join(samples_dir, file))
                if feature is not None:
                    features.append(feature)
                    labels.append(0)  # 0 para outras vozes

        if len(features) < 5:
            log_message("Poucas amostras para treinamento.", 'warning')
            return False

        X = np.array(features)
        y = np.array(labels)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)

        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        log_message(f"Modelo de voz treinado com acurácia: {accuracy:.2f}")

        # Criar diretório se não existir
        os.makedirs(MODEL_SAVE_PATH, exist_ok=True)
        joblib.dump(self.model, f"{MODEL_SAVE_PATH}voice_model.pkl")
        return True

    def load_model(self):
        """Carrega o modelo treinado."""
        try:
            self.model = joblib.load(f"{MODEL_SAVE_PATH}voice_model.pkl")
            log_message("Modelo de reconhecimento de voz carregado.")
        except FileNotFoundError:
            log_message("Modelo de voz não encontrado.")

    def verify_voice(self, audio_data):
        """Verifica se a voz é do usuário autorizado."""
        if self.model is None:
            return True  # Se não há modelo, aceita qualquer voz

        # Salvar áudio temporário
        import sounddevice as sd
        import scipy.io.wavfile as wav

        fs = 22050
        filename = f"{DATA_PATH}temp_voice.wav"
        wav.write(filename, fs, audio_data)

        feature = self.extract_features(filename)
        os.remove(filename)

        if feature is not None:
            prediction = self.model.predict([feature])
            return prediction[0] == 1
        return False
