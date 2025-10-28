import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import log_message

class AIAPI:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        log_message("API Gemini configurada.")

    def generate_response(self, prompt, context=""):
        """Gera uma resposta usando Gemini."""
        try:
            full_prompt = f"Contexto: {context}\n\nPrompt: {prompt}\n\nResponda como Frieren, a maga elfa de Sousou no Frieren, de forma amigável e útil. Sempre responda em português brasileiro."
            response = self.model.generate_content(full_prompt)
            log_message(f"Resposta gerada: {response.text}")
            return response.text
        except Exception as e:
            log_message(f"Erro ao gerar resposta: {e}", 'error')
            return "Desculpe, não consegui processar isso agora."

    def learn_from_unknown(self, command, context=""):
        """Aprende com comandos desconhecidos."""
        prompt = f"Comando desconhecido: '{command}'. Contexto visual: {context}. Sugira como responder ou o que fazer."
        suggestion = self.generate_response(prompt)
        log_message(f"Sugestão para comando desconhecido: {suggestion}")
        return suggestion
