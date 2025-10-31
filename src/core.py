import threading
import time
from concurrent.futures import ThreadPoolExecutor

# Fix imports for running from src/ directory
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from voice import VoiceAssistant
from ai_api import AIAPI
from voice_recognition import VoiceRecognition
from utils import setup_logging, log_message
from config import WAKE_WORD
from commands import open_apps, manage_apps

class StarkCore:
    def __init__(self):
        setup_logging()
        self.voice = VoiceAssistant()
        self.ai = AIAPI()
        self.voice_recog = VoiceRecognition()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def handle_command_async(self, command):
        """Processa comando de forma assíncrona."""
        def _process():
            try:
                if self._try_local_commands(command):
                    return
                self._fallback_to_ai(command)
            except Exception as e:
                log_message(f"Erro processando comando: {e}")
                self.voice.speak("Erro interno. Tente novamente.")

        self.executor.submit(_process)

    def _try_local_commands(self, command):
        """Tenta comandos locais organizados."""
        if open_apps.handle_open_command(command, self.voice):
            return True
        if manage_apps.handle_add_app_command(command, self.voice):
            return True
        if manage_apps.handle_list_apps_command(command, self.voice):
            return True

        # Comandos de chat
        if 'vamos conversar' in command or 'modo chat' in command or 'conversar' in command:
            self._start_chat_mode()
            return True

        # Comandos para sair do chat (mais variações naturais)
        exit_commands = [
            'sair do chat', 'parar conversa', 'encerrar chat',
            'pode fechar o chat', 'pode parar a conversa', 'ta bom', 'pode parar',
            'chega', 'encerra', 'para ai', 'para com isso', 'fecha o chat'
        ]
        if any(exit_cmd in command for exit_cmd in exit_commands):
            self._end_chat_mode()
            return True

        if 'gravar voz' in command or 'treinar voz' in command:
            self._handle_voice_training()
            return True

        if 'sair' in command or 'parar' in command:
            self.voice.speak("Até logo!")
            return False

        if 'estatísticas' in command or 'stats' in command or 'uso' in command:
            self._show_usage_stats()
            return True

        return False

    def _start_chat_mode(self):
        """Inicia o modo de chat multi-turn."""
        if self.ai.start_chat_session():
            self.voice.speak("Modo conversa ativado! Agora podemos conversar naturalmente. Diga 'sair do chat' quando quiser parar.")
            log_message("Modo chat iniciado")
        else:
            self.voice.speak("Erro ao iniciar modo conversa.")

    def _end_chat_mode(self):
        """Encerra o modo de chat."""
        if self.ai.end_chat_session():
            self.voice.speak("Modo conversa encerrado. Voltando ao modo normal.")
            log_message("Modo chat encerrado")
            return True
        else:
            self.voice.speak("Erro ao encerrar modo conversa.")
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

    def _show_usage_stats(self):
        """Mostra estatísticas de uso da API."""
        try:
            stats = self.ai.get_usage_stats()
            message = f"Estatísticas de uso: {stats['today_requests']} requests hoje, {stats['total_requests']} total. Uso RPM: {stats['rpm_usage_percent']:.1f}%, TPM: {stats['tpm_usage_percent']:.1f}%."
            self.voice.speak(message)
            log_message(f"Estatísticas mostradas: {message}")
        except Exception as e:
            log_message(f"Erro ao mostrar estatísticas: {e}", 'error')
            self.voice.speak("Erro ao obter estatísticas de uso.")

    def _fallback_to_ai(self, command):
        """Fallback inteligente com AI (Gemini/Ollama)."""
        command_lower = command.lower()

        # Verificar se está em modo chat
        if self.ai.is_chat_mode_active():
            log_message(f"Mensagem de chat recebida: '{command}'")
            response = self.ai.send_chat_message(command)
            self.voice.speak(response)
            return

        # Verificar se é comando direto para Gemini
        if 'gemini' in command_lower:
            # Ativar automaticamente modo chat quando usar Gemini
            if not self.ai.is_chat_mode_active():
                log_message("Ativando modo chat automaticamente para comando Gemini")
                self._start_chat_mode()

            # Extrair query após "gemini"
            gemini_index = command_lower.find('gemini')
            query = command[gemini_index + 6:].strip()  # +6 para pular "gemini"

            if query:
                log_message(f"Comando Gemini detectado. Query: '{query}'")
                response, generation_time = self.ai.generate_gemini_direct(query)
                self.voice.speak(f"Consultando Gemini: {response}")
                return
            else:
                self.voice.speak("Você disse 'gemini' mas não especificou o que perguntar.")
                return

        # Comando normal para Stark
        prompt = f"Usuário disse: '{command}'. Interprete como comando para IA assistente. Se for abrir app ou tarefa, diga claramente. Se ambíguo, pergunte o que fazer. Responda em português brasileiro."
        response, generation_time = self.ai.generate_response(prompt)
        self.voice.speak(response)



    def start_voice_loop(self):
        """Loop de voz em thread separada."""
        def voice_worker():
            while True:
                try:
                    # Verificar se está em modo chat
                    if self.ai.is_chat_mode_active():
                        # Modo chat: ouvir continuamente sem wake word
                        log_message("Modo chat ativo - ouvindo continuamente...")
                        command = self.voice.listen()
                        if command:
                            log_message(f"Comando de chat recebido: '{command}'")
                            self.handle_command_async(command)
                        time.sleep(0.1)  # Pequena pausa para não sobrecarregar
                    else:
                        # Modo normal: aguardar wake word
                        command = self.voice.listen_for_wake_word()
                        if command:
                            self.handle_command_async(command)
                            time.sleep(0.1)

                except Exception as e:
                    log_message(f"Erro no loop de voz: {e}")
                    time.sleep(1)

        threading.Thread(target=voice_worker, daemon=True).start()

    def run(self):
        """Inicia Stark AI com threads paralelas."""
        log_message("Stark AI iniciando...")
        self.voice.speak("Sistema STARK iniciado. Diga 'STARK' para me chamar.")

        self.start_voice_loop()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            log_message("Stark AI finalizado.")
            self.executor.shutdown()
