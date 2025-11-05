
# Configurações da IA Assistente Stark


VOICE_LANGUAGE = 'pt-BR'  # Idioma para reconhecimento e síntese de voz
VOICE_RATE = 200  # Velocidade da fala (palavras por minuto)
VOICE_VOLUME = 1.0  # Volume da fala (0.0 a 1.0)
WAKE_WORD = 'stark'  # Palavra de ativação


MODEL_SAVE_PATH = '../models/'  # Caminho para salvar modelos treinados
DATA_PATH = '../data/'  # Caminho para dados de treinamento


SCREEN_CAPTURE_INTERVAL = 1/60  # Intervalo de captura de tela (60 FPS)


GEMINI_API_KEY = 'AIzaSyDDL3nrf5qYsIpdpNmTwFkvrRfqXpoOwIU'  

# Configurações de IA - Priorizando modelos gratuitos e rápidos
GEMINI_MODEL = 'models/gemini-2.0-flash'  # Modelo principal (mais rápido e gratuito)
GEMINI_MODELS = [
    'models/gemini-2.0-flash',      # Principal: rápido e gratuito
    'models/gemini-1.5-flash',      # Backup: ainda gratuito e rápido
    'models/gemini-1.5-pro'         # Último recurso: mais inteligente mas limitado
]

# Configurações Ollama (para futuro uso local)
OLLAMA_API_URL = 'http://localhost:11434'  # URL padrão do Ollama
OLLAMA_MODEL = 'mistral:7b'  # Modelo padrão (pode ser mudado para llama3.2:3b)
OLLAMA_SYSTEM_PROMPT = """Você é Stark, um assistente de IA brasileiro amigável e útil.
Suas especialidades são:
1. Programação básica (Python, JavaScript, C#)
2. Jogos e guias de jogos (sem boatos)
3. Pesquisa geral e conhecimento factual

Sempre responda em português brasileiro de forma direta, amigável e concisa.
Seja prestativo e demonstre conhecimento nas suas áreas de especialidade."""


AI_STRATEGY = 'gemini_first'  # Começar com Gemini por ser mais rápido

# Configurações de cache
MAX_CACHE_VARIATIONS = 3  # Máximo de variações por prompt
CACHE_VARIATION_CHANCE = 0.3  # Chance de gerar variação (30%)

# Outras configurações
LOG_FILE = 'Stark.log'  # Arquivo de log
DEBUG_MODE = True  # Modo de depuração
