import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import difflib
import json
import os
from config import VOICE_LANGUAGE, VOICE_RATE, VOICE_VOLUME, WAKE_WORD, DATA_PATH
from utils import log_message
from voice_recognition import VoiceRecognition

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 100  # Ainda mais sensível
        self.recognizer.dynamic_energy_threshold = True  # Ajuste dinâmico ao ambiente
        self.recognizer.pause_threshold = 1  # Menor pausa para detectar fim da fala
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', VOICE_RATE)
        self.engine.setProperty('volume', VOICE_VOLUME)
        self.wake_word = WAKE_WORD.lower()
        # Configurar voz masculina em português
        voices = self.engine.getProperty('voices')
        male_voice = None
        for voice in voices:
            if 'male' in voice.name.lower() and ('portuguese' in voice.name.lower() or 'brazilian' in voice.name.lower() or 'pt' in voice.name.lower()):
                male_voice = voice
                break
        if not male_voice:
            # Fallback para qualquer voz masculina
            for voice in voices:
                if 'male' in voice.name.lower():
                    male_voice = voice
                    break
        if male_voice:
            self.engine.setProperty('voice', male_voice.id)
            log_message(f"Voz masculina selecionada: {male_voice.name}")
        else:
            # Como não há voz masculina, usar voz feminina padrão (Maria)
            for voice in voices:
                if 'maria' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    log_message(f"Voz feminina Maria selecionada: {voice.name}")
                    break
            else:
                log_message("Nenhuma voz conhecida encontrada, usando padrão.")
                self.engine.setProperty('voice', VOICE_LANGUAGE)

    def listen(self):
        """Escuta e reconhece fala do usuário."""
        with sr.Microphone() as source:
            log_message("Escutando...")
            self.recognizer.adjust_for_ambient_noise(source, duration=2)
            audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
            try:
                text = self.recognizer.recognize_google(audio, language=VOICE_LANGUAGE)
                log_message(f"Fala reconhecida: {text}")
                return text.lower()
            except sr.UnknownValueError:
                log_message("Não entendi a fala.", 'warning')
                return None
            except sr.RequestError:
                log_message("Erro na requisição de reconhecimento.", 'error')
                return None

    def speak(self, text):
        """Sintetiza e fala o texto."""
        log_message(f"Falando: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_wake_word(self):
        """Escuta por wake word com timeout curto usando Google (mais rápido e preciso)."""
        try:
            mic = sr.Microphone()
            with mic as source:
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)  # Timeout maior, phrase menor para mais rapidez
                # Usar Google diretamente (mais rápido que Vosk/Sphinx)
                text = self.recognizer.recognize_google(audio, language=VOICE_LANGUAGE)
                # Só logar quando detectar algo
                if text:
                    log_message(f"Fala reconhecida para wake word: '{text}'")
                    log_message(f"Procurando wake word '{self.wake_word}' em: '{text.lower()}'")
                return text.lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            log_message("Erro na requisição de reconhecimento para wake word.", 'error')
            return None
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            log_message(f"Erro no microfone wake word: {e}", 'error')
            return None

    def listen_for_wake_word(self):
        """Escuta por wake word 'Frieren' silenciosamente e permite comandos em sequência."""
        # Carrega variações treinadas da voz do usuário
        user_variations = self.load_user_variations()

        while True:
            text = self.listen_wake_word()
            if text:
                text_lower = text.lower()
                detected = False

                # Primeiro verifica variações treinadas do usuário
                if user_variations:
                    for variation in user_variations:
                        if variation in text_lower or difflib.SequenceMatcher(None, text_lower, variation).ratio() > 0.7:
                            detected = True
                            log_message(f"Wake word detectado (treinado): '{text}' -> '{variation}'")
                            break

                # Se não encontrou nas variações treinadas, usa lógica padrão
                if not detected:
                    if self.wake_word in text_lower or difflib.SequenceMatcher(None, text_lower, self.wake_word).ratio() > 0.6:
                        detected = True
                        log_message(f"Wake word detectado (padrão): {text}")

                if detected:
                    # Extrai comando após wake word, ou usa a frase inteira se não encontrar
                    command = self.extract_command(text_lower)
                    if command:
                        return command
                    else:
                        # Se não há comando claro, escuta separado
                        command = self.listen()
                        return command
                else:
                    log_message(f"Texto ouvido mas não é wake word: '{text}'")

    def load_user_variations(self):
        """Carrega variações treinadas da voz do usuário."""
        try:
            variations_file = f"{DATA_PATH}frieren_variations.txt"
            if os.path.exists(variations_file):
                with open(variations_file, 'r', encoding='utf-8') as f:
                    return [line.strip().lower() for line in f if line.strip()]
        except Exception as e:
            log_message(f"Erro ao carregar variações: {e}", 'warning')
        return []

    def extract_command(self, text_lower):
        """Extrai comando da frase, tentando diferentes abordagens."""
        # Remove variações conhecidas de 'frieren'
        for variation in [self.wake_word] + self.load_user_variations():
            if variation in text_lower:
                command = text_lower.replace(variation, '').strip()
                if command:
                    return command

        # Se não encontrou, usa similaridade para remover parte mais próxima
        if difflib.SequenceMatcher(None, text_lower, self.wake_word).ratio() > 0.6:
            # Assume que a primeira palavra similar é o wake word
            words = text_lower.split()
            if words:
                # Remove primeira palavra se for similar ao wake word
                first_word = words[0]
                if difflib.SequenceMatcher(None, first_word, self.wake_word).ratio() > 0.5:
                    return ' '.join(words[1:]).strip()

        return text_lower.strip()

    def confirm_action(self, action):
        """Confirma uma ação com o usuário."""
        self.speak(f"Você disse: {action}. Está correto?")
        response = self.listen()
        if response and ('sim' in response or 'yes' in response):
            return True
        return False
