import google.generativeai as genai
from config import GEMINI_API_KEY
from utils import log_message

class AIAPI:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        # Usar modelo disponível
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            log_message("API Gemini configurada com gemini-2.5-flash.")
        except Exception as e:
            log_message(f"Erro ao configurar Gemini: {e}", 'error')
            self.model = None

    def generate_response(self, prompt, context=""):
        """Gera uma resposta usando Gemini."""
        if not self.model:
            return "API Gemini não configurada."
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

    def generate_learning_question(self, contexts):
        """Gera perguntas de aprendizado baseadas em observações."""
        if not self.model:
            return "O que você está fazendo agora?"
        try:
            prompt = f"Baseado nestas observações da tela: {contexts}. Gere uma pergunta inteligente para aprender mais sobre os padrões de uso do usuário. Foque em entender o que ele está fazendo e por quê."
            response = self.model.generate_content(prompt)
            question = response.text.strip()
            log_message(f"Pergunta de aprendizado gerada: {question}")
            return question
        except Exception as e:
            log_message(f"Erro ao gerar pergunta de aprendizado: {e}", 'error')
            return "O que você está fazendo agora?"

    def learn_from_response(self, question, response, observations):
        """Aprende com respostas do usuário."""
        if not self.model:
            return
        try:
            prompt = f"Pergunta feita: {question}\nResposta do usuário: {response}\nObservações anteriores: {observations}\nAnalise esta interação e extraia padrões de comportamento do usuário para melhorar futuras interações."
            analysis = self.model.generate_content(prompt)
            log_message(f"Análise de aprendizado: {analysis.text}")
            # Aqui poderia salvar em um banco de dados ou arquivo para aprendizado futuro
        except Exception as e:
            log_message(f"Erro ao aprender com resposta: {e}", 'error')
