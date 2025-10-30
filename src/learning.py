import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from config import MODEL_SAVE_PATH, DATA_PATH
from utils import log_message

class LearningModule:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Carrega o modelo treinado se existir."""
        model_path = f"{MODEL_SAVE_PATH}intent_model.pkl"
        try:
            self.model = joblib.load(model_path)
            log_message("Modelo carregado com sucesso.")
        except FileNotFoundError:
            log_message("Modelo não encontrado, será treinado posteriormente.")
            self.model = None

    def train_intent_classifier(self, data_file=f"{DATA_PATH}intents.csv"):
        """Treina um classificador de intenções."""
        try:
            data = pd.read_csv(data_file)
            X = data['text'].values
            y = data['intent'].values

            # Simples bag-of-words (pode ser melhorado com TF-IDF ou embeddings)
            from sklearn.feature_extraction.text import CountVectorizer
            vectorizer = CountVectorizer()
            X_vectorized = vectorizer.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            predictions = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, predictions)
            log_message(f"Modelo treinado com acurácia: {accuracy:.2f}")

            # Salvar modelo e vectorizer
            joblib.dump(self.model, f"{MODEL_SAVE_PATH}intent_model.pkl")
            joblib.dump(vectorizer, f"{MODEL_SAVE_PATH}vectorizer.pkl")

        except Exception as e:
            log_message(f"Erro ao treinar modelo: {e}", 'error')

    def predict_intent(self, text):
        """Prevê a intenção de um texto."""
        if self.model is None:
            return None
        try:
            vectorizer = joblib.load(f"{MODEL_SAVE_PATH}vectorizer.pkl")
            text_vectorized = vectorizer.transform([text])
            intent = self.model.predict(text_vectorized)[0]
            log_message(f"Intenção prevista: {intent}")
            return intent
        except Exception as e:
            log_message(f"Erro ao prever intenção: {e}", 'error')
            return None

    def save_interaction(self, text, intent, data_file=f"{DATA_PATH}intents.csv"):
        """Salva uma interação para re-treinamento futuro."""
        try:
            new_data = pd.DataFrame({'text': [text], 'intent': [intent]})
            new_data.to_csv(data_file, mode='a', header=False, index=False)
            log_message("Interação salva para aprendizado.")
        except Exception as e:
            log_message(f"Erro ao salvar interação: {e}", 'error')
