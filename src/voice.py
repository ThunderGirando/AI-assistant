import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import difflib
from config import VOICE_LANGUAGE, VOICE_RATE, VOICE_VOLUME, WAKE_WORD
from utils import log_message
from voice_recognition import VoiceRecognition

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Baixar threshold para mais sensibilidade (padrão ~300)
        self.recognizer.dynamic_energy_threshold = True  # Ajuste dinâmico ao ambiente
        self.recognizer.pause_threshold = 1  # Menor pausa para detectar fim da fala
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', VOICE_RATE)
        self.engine.setProperty('volume', VOICE_VOLUME)
        self.wake_word = WAKE_WORD.lower()
        # Configurar voz feminina em português
        voices = self.engine.getProperty('voices')
        female_voice = None
        for voice in voices:
            if 'female' in voice.name.lower() and ('portuguese' in voice.name.lower() or 'brazilian' in voice.name.lower() or 'pt' in voice.name.lower()):
                female_voice = voice
                break
        if not female_voice:
            # Fallback para qualquer voz feminina
            for voice in voices:
                if 'female' in voice.name.lower():
                    female_voice = voice
                    break
        if female_voice:
            self.engine.setProperty('voice', female_voice.id)
            log_message(f"Voz feminina selecionada: {female_voice.name}")
        else:
            log_message("Voz feminina não encontrada, usando padrão.")
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
        """Escuta por wake word com timeout curto."""
        with sr.Microphone() as source:
            # Não logar constantemente para não poluir o console
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)  # Aumentei timeout e phrase_time_limit
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

    def listen_for_wake_word(self):
        """Escuta por wake word 'Frieren' silenciosamente e permite comandos em sequência."""
        while True:
            text = self.listen_wake_word()
            if text:
                text_lower = text.lower()
                # Verifica se começa com wake word (com tolerância de 70% para mais flexibilidade)
                if text_lower.startswith(self.wake_word[:3]) and difflib.SequenceMatcher(None, text_lower[:len(self.wake_word)], self.wake_word).ratio() > 0.7:
                    log_message(f"Wake word detectado: {text}")
                    # Extrai comando após wake word
                    command = text_lower[len(self.wake_word):].strip()
                    if command:
                        return command
                    else:
                        # Se não há comando, escuta separado
                        command = self.listen()
                        return command
                else:
                    log_message(f"Texto ouvido mas não é wake word: '{text}'")

    def confirm_action(self, action):
        """Confirma uma ação com o usuário."""
        self.speak(f"Você disse: {action}. Está correto?")
        response = self.listen()
        if response and ('sim' in response or 'yes' in response):
            return True
        return False
