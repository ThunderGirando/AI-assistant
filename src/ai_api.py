import google.generativeai as genai
import requests
import json
import time
import hashlib
import os
import random
from datetime import datetime, timedelta
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_MODELS, OLLAMA_API_URL, OLLAMA_MODEL, OLLAMA_SYSTEM_PROMPT, AI_STRATEGY, MAX_CACHE_VARIATIONS, CACHE_VARIATION_CHANCE
from utils import log_message

class AIAPI:
    def __init__(self):
        # Configurar Gemini diretamente com modelo otimizado
        genai.configure(api_key=GEMINI_API_KEY)
        try:
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            log_message(f"API Gemini configurada com {GEMINI_MODEL}.")
            self.chat_session = None  # Para modo chat multi-turn
        except Exception as e:
            log_message(f"Erro ao configurar Gemini: {e}", 'error')
            self.model = None
            self.chat_session = None

        # Configurações Ollama
        self.ollama_url = OLLAMA_API_URL
        self.ollama_model = OLLAMA_MODEL
        self.ollama_system = OLLAMA_SYSTEM_PROMPT
        self.ollama_available = self._check_ollama_status()

        # Estratégia de IA
        self.ai_strategy = AI_STRATEGY

        # Sistema de cache para respostas
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.response_cache = {}  # Cache em memória para sessão atual

        # Sistema de histórico de conversas para evitar repetições
        self.conversation_history = []  # Lista de tuplas (prompt, response, timestamp)
        self.max_history_size = 50  # Máximo de conversas para manter em memória

        # Carregar cache existente na inicialização
        self._load_existing_cache()

        # Sistema de monitoramento de uso da API
        self.usage_dir = os.path.join(os.path.dirname(__file__), '..', 'usage')
        os.makedirs(self.usage_dir, exist_ok=True)
        self.usage_stats = self._load_usage_stats()

    def _check_ollama_status(self):
        """Verifica se Ollama está rodando."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _generate_ollama_response(self, prompt, context=""):
        """Gera resposta usando Ollama."""
        if not self.ollama_available:
            return None

        try:
            full_prompt = f"Contexto: {context}\n\n{prompt}"
            payload = {
                "model": self.ollama_model,
                "prompt": full_prompt,
                "system": self.ollama_system,
                "stream": False
            }
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                log_message(f"Resposta Ollama gerada: {result['response'][:100]}...")
                return result['response']
            else:
                log_message(f"Erro na API Ollama: {response.status_code}", 'error')
                return None
        except Exception as e:
            log_message(f"Erro ao gerar resposta Ollama: {e}", 'error')
            return None

    def _generate_gemini_response(self, prompt, context="", model_index=0):
        """Gera resposta usando Gemini com hierarquia de modelos e fallback automático."""
        if model_index >= len(self.gemini_models):
            log_message("Todos os modelos Gemini falharam", 'error')
            return "Desculpe, não consegui processar isso agora. Todos os modelos estão indisponíveis."

        model_name = self.gemini_models[model_index]

        try:
            model = genai.GenerativeModel(model_name)
            full_prompt = f"Contexto: {context}\n\nPrompt: {prompt}\n\nVocê é Stark, um assistente de voz brasileiro. Responda de forma direta, amigável e concisa. Sempre em português brasileiro."
            response = model.generate_content(full_prompt)
            log_message(f"Resposta Gemini ({model_name}) gerada: {response.text[:100]}...")
            # Reset para o modelo principal em caso de sucesso
            self.current_gemini_index = 0
            return response.text
        except Exception as e:
            error_msg = str(e).lower()
            # Verificar se é erro de rate limit ou quota
            is_rate_limit = ('rate limit' in error_msg or 'quota' in error_msg or '429' in error_msg)

            if is_rate_limit and model_index < len(self.gemini_models) - 1:
                # Tentar próximo modelo na hierarquia
                next_model = self.gemini_models[model_index + 1]
                log_message(f"Rate limit em {model_name}, tentando {next_model}...", 'warning')
                time.sleep(1)  # Pequena pausa antes do retry
                return self._generate_gemini_response(prompt, context, model_index + 1)
            else:
                log_message(f"Erro ao gerar resposta Gemini ({model_name}): {e}", 'error')
                return "Desculpe, não consegui processar isso agora."

    def _get_cache_key(self, prompt, context=""):
        """Gera chave única para cache baseada no prompt e contexto."""
        content = f"{prompt}|{context}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def _load_existing_cache(self):
        """Carrega todo o cache existente em memória na inicialização."""
        if not os.path.exists(self.cache_dir):
            return

        loaded_count = 0
        expired_count = 0

        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)

                    # Cache permanente - sem expiração
                    cache_key = filename[:-5]  # Remove .json

                    # Verifica se é cache antigo (única resposta) ou novo (múltiplas variações)
                    if isinstance(cached_data['response'], list):
                        # Novo formato: lista de variações
                        self.response_cache[cache_key] = cached_data['response']
                    else:
                        # Formato antigo: converte para lista
                        self.response_cache[cache_key] = [cached_data['response']]

                    loaded_count += 1

                except Exception as e:
                    log_message(f"Erro ao carregar cache {filename}: {e}", 'warning')
                    expired_count += 1

        if loaded_count > 0:
            log_message(f"Cache carregado: {loaded_count} respostas em memória")
        if expired_count > 0:
            log_message(f"Cache corrompido removido: {expired_count} arquivos", 'warning')

    def _load_cached_response(self, cache_key):
        """Carrega resposta do cache se existir."""
        # Primeiro verifica cache em memória
        if cache_key in self.response_cache:
            log_message("Resposta carregada do cache em memória")
            return self.response_cache[cache_key]

        # Depois verifica cache em arquivo (fallback para compatibilidade)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    # Cache permanente - sem expiração
                    log_message("Resposta carregada do cache em arquivo")
                    # Move para memória para próximas consultas
                    self.response_cache[cache_key] = cached_data['response']
                    return cached_data['response']
            except Exception as e:
                log_message(f"Erro ao carregar cache: {e}", 'warning')

        return None

    def _save_cached_response(self, cache_key, response):
        """Salva resposta no cache permanentemente."""
        # Salva em memória
        self.response_cache[cache_key] = response

        # Salva em arquivo (permanente, sem timestamp de expiração)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'response': response,
                    'timestamp': time.time()  # Mantém timestamp para metadados
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_message(f"Erro ao salvar cache: {e}", 'warning')

    def clear_cache(self, pattern=None):
        """Limpa cache baseado em padrão opcional."""
        if pattern:
            # Remove entradas que contenham o padrão
            keys_to_remove = [k for k in self.response_cache.keys() if pattern.lower() in k.lower()]
            for key in keys_to_remove:
                del self.response_cache[key]
                cache_file = os.path.join(self.cache_dir, f"{key}.json")
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                    except:
                        pass
            log_message(f"Cache limpo: {len(keys_to_remove)} entradas removidas com padrão '{pattern}'")
        else:
            # Limpa todo o cache
            cache_count = len(self.response_cache)
            self.response_cache.clear()

            # Remove arquivos
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        try:
                            os.remove(os.path.join(self.cache_dir, filename))
                        except:
                            pass
            log_message(f"Cache completamente limpo: {cache_count} entradas removidas")

    def get_cache_stats(self):
        """Retorna estatísticas do cache."""
        memory_count = len(self.response_cache)
        file_count = 0
        if os.path.exists(self.cache_dir):
            file_count = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])

        return {
            'memory_cache': memory_count,
            'file_cache': file_count,
            'total': memory_count + file_count
        }

    def generate_response(self, prompt, context="", use_cache=True):
        """Gera resposta usando Gemini diretamente com cache inteligente e histórico de conversas."""
        if not self.model:
            return "API Gemini não configurada."

        # Verifica se é uma repetição baseada no histórico
        similar_response = self._check_conversation_history(prompt)
        if similar_response:
            log_message("Resposta similar encontrada no histórico, reutilizando...")
            return similar_response, 0.0

        # Verifica cache primeiro
        if use_cache:
            cache_key = self._get_cache_key(prompt, context)
            cached_response = self._load_cached_response(cache_key)
            if cached_response:
                return cached_response

        try:
            full_prompt = f"Contexto: {context}\n\nPrompt: {prompt}\n\nVocê é Stark, um assistente de voz brasileiro. Responda de forma direta, amigável e concisa. Sempre em português brasileiro."

            # Medir tempo de geração
            start_time = time.time()
            response = self.model.generate_content(full_prompt)
            end_time = time.time()
            generation_time = end_time - start_time

            log_message(f"Resposta Gemini gerada em {generation_time:.2f}s: {response.text[:100]}...")
            result = response.text

            # Adiciona ao histórico de conversas
            self._add_to_conversation_history(prompt, result)

            # Salva no cache
            if use_cache:
                self._save_cached_response(cache_key, result)

            return result, generation_time
        except Exception as e:
            log_message(f"Erro ao gerar resposta Gemini: {e}", 'error')
            return "Desculpe, não consegui processar isso agora.", 0.0

    def generate_gemini_direct(self, query, context=""):
        """Gera resposta direta do Gemini sem cache, otimizada para perguntas específicas."""
        if not self.model:
            return "API Gemini não configurada.", 0.0

        try:
            # Primeiro, adaptar a query para uma pergunta real usando IA
            adapt_prompt = f"Transforme esta query em uma pergunta clara e completa: '{query}'. Faça uma pergunta educacional e bem formulada em português brasileiro."

            start_time = time.time()
            adapt_response = self.model.generate_content(adapt_prompt)
            adapted_question = adapt_response.text.strip()

            # Agora fazer a pergunta real ao Gemini
            full_prompt = f"Contexto: {context}\n\nPergunta: {adapted_question}\n\nResponda de forma direta, clara e completa. Sempre em português brasileiro."

            response = self.model.generate_content(full_prompt)
            end_time = time.time()
            generation_time = end_time - start_time

            log_message(f"Resposta Gemini direta gerada em {generation_time:.2f}s: {response.text[:100]}...")
            result = response.text

            # Verificar se a query é sensível ao tempo (não deve ser cacheada)
            is_time_sensitive = self._is_time_sensitive_query(adapted_question.lower())

            if not is_time_sensitive:
                # Salvar no cache para futuras consultas similares
                cache_key = self._get_cache_key(adapted_question, context)
                log_message(f"Salvando resposta no cache com chave: {cache_key}")
                self._save_cached_response(cache_key, result)
            else:
                log_message("Query sensível ao tempo detectada - pulando cache")

            # Adicionar ao histórico de conversas
            self._add_to_conversation_history(adapted_question, result)

            return result, generation_time
        except Exception as e:
            log_message(f"Erro ao gerar resposta Gemini direta: {e}", 'error')
            return "Desculpe, não consegui processar isso agora.", 0.0

    def _is_simple_question(self, prompt):
        """Determina se uma pergunta é simples baseada em heurísticas."""
        prompt_lower = prompt.lower()

        # Perguntas simples: saudações, comandos básicos, perguntas factuais diretas
        simple_keywords = [
            'oi', 'olá', 'bom dia', 'boa tarde', 'boa noite',
            'como vai', 'tudo bem', 'qual é', 'o que é', 'quem é',
            'quanto é', 'quando', 'onde', 'por que', 'como',
            'explique', 'defina', 'significa', 'exemplo',
            'sim', 'não', 'verdadeiro', 'falso'
        ]

        # Conta palavras simples
        simple_words = sum(1 for word in simple_keywords if word in prompt_lower)

        # Perguntas curtas (< 15 palavras) ou com muitas palavras simples são consideradas simples
        word_count = len(prompt.split())
        return word_count < 15 or simple_words > 2

    def _is_time_sensitive_query(self, query):
        """Determina se uma query é sensível ao tempo e não deve ser cacheada."""
        time_keywords = [
            'hoje', 'ontem', 'amanhã', 'agora', 'hora', 'horas',
            'minuto', 'minutos', 'segundo', 'segundos', 'dia', 'dias',
            'semana', 'semanas', 'mês', 'meses', 'ano', 'anos',
            'atual', 'atualmente', 'recente', 'recentemente',
            'último', 'última', 'últimos', 'últimas',
            'próximo', 'próxima', 'próximos', 'próximas',
            'que dia', 'que hora', 'que mês', 'que ano',
            'data', 'tempo', 'clima', 'previsão',
            'notícia', 'notícias', 'atualização', 'atualizações'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in time_keywords)

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

    def _load_usage_stats(self):
        """Carrega estatísticas de uso da API."""
        usage_file = os.path.join(self.usage_dir, 'usage_stats.json')
        if os.path.exists(usage_file):
            try:
                with open(usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                log_message(f"Erro ao carregar estatísticas de uso: {e}", 'warning')

        # Estatísticas padrão se arquivo não existir
        return {
            'total_requests': 0,
            'total_tokens': 0,
            'daily_requests': {},
            'daily_tokens': {},
            'last_reset': datetime.now().isoformat()
        }

    def _save_usage_stats(self):
        """Salva estatísticas de uso da API."""
        usage_file = os.path.join(self.usage_dir, 'usage_stats.json')
        try:
            with open(usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log_message(f"Erro ao salvar estatísticas de uso: {e}", 'warning')

    def _update_usage_stats(self, tokens_used=0):
        """Atualiza estatísticas de uso da API."""
        today = datetime.now().date().isoformat()

        # Inicializar dia se necessário
        if today not in self.usage_stats['daily_requests']:
            self.usage_stats['daily_requests'][today] = 0
        if today not in self.usage_stats['daily_tokens']:
            self.usage_stats['daily_tokens'][today] = 0

        # Atualizar contadores
        self.usage_stats['total_requests'] += 1
        self.usage_stats['total_tokens'] += tokens_used
        self.usage_stats['daily_requests'][today] += 1
        self.usage_stats['daily_tokens'][today] += tokens_used

        # Salvar automaticamente
        self._save_usage_stats()

    def _check_conversation_history(self, prompt):
        """Verifica se o prompt é exatamente igual a conversas anteriores e retorna resposta se encontrada."""
        if not self.conversation_history:
            return None

        prompt_lower = prompt.lower().strip()

        # Verificar apenas prompts exatamente iguais
        for prev_prompt, prev_response, timestamp in reversed(self.conversation_history[-5:]):  # Últimas 5 conversas
            prev_prompt_lower = prev_prompt.lower().strip()

            if prompt_lower == prev_prompt_lower and time.time() - timestamp < 300:  # 5 minutos
                log_message(f"Pergunta idêntica encontrada no histórico -> reutilizando resposta")
                return prev_response

        return None

    def _add_to_conversation_history(self, prompt, response):
        """Adiciona uma conversa ao histórico."""
        self.conversation_history.append((prompt, response, time.time()))

        # Manter apenas as últimas conversas
        if len(self.conversation_history) > self.max_history_size:
            self.conversation_history = self.conversation_history[-self.max_history_size:]

    def get_usage_stats(self):
        """Retorna estatísticas de uso da API."""
        today = datetime.now().date().isoformat()

        # Limpar dados antigos (manter apenas últimos 30 dias)
        cutoff_date = (datetime.now() - timedelta(days=30)).date().isoformat()

        # Filtrar dados antigos
        self.usage_stats['daily_requests'] = {
            k: v for k, v in self.usage_stats['daily_requests'].items() if k >= cutoff_date
        }
        self.usage_stats['daily_tokens'] = {
            k: v for k, v in self.usage_stats['daily_tokens'].items() if k >= cutoff_date
        }

        # Calcular estatísticas atuais
        today_requests = self.usage_stats['daily_requests'].get(today, 0)
        today_tokens = self.usage_stats['daily_tokens'].get(today, 0)

        # Estimar uso baseado nos limites gratuitos
        rpm_limit = 15  # requests per minute
        tpm_limit = 1000000  # tokens per minute (1M)

        rpm_usage_percent = (today_requests / rpm_limit) * 100 if rpm_limit > 0 else 0
        tpm_usage_percent = (today_tokens / tpm_limit) * 100 if tpm_limit > 0 else 0

        return {
            'total_requests': self.usage_stats['total_requests'],
            'total_tokens': self.usage_stats['total_tokens'],
            'today_requests': today_requests,
            'today_tokens': today_tokens,
            'rpm_usage_percent': rpm_usage_percent,
            'tpm_usage_percent': tpm_usage_percent,
            'rpm_limit': rpm_limit,
            'tpm_limit': tpm_limit,
            'last_reset': self.usage_stats.get('last_reset', 'N/A')
        }

    def start_chat_session(self):
        """Inicia uma sessão de chat multi-turn."""
        if not self.model:
            return False

        try:
            self.chat_session = self.model.start_chat(history=[])
            log_message("Sessão de chat multi-turn iniciada")
            return True
        except Exception as e:
            log_message(f"Erro ao iniciar sessão de chat: {e}", 'error')
            return False

    def end_chat_session(self):
        """Encerra a sessão de chat atual."""
        if self.chat_session:
            self.chat_session = None
            log_message("Sessão de chat encerrada")
            return True
        return False

    def is_chat_mode_active(self):
        """Verifica se o modo chat está ativo."""
        return self.chat_session is not None

    def send_chat_message(self, message, context=""):
        """Envia mensagem na sessão de chat ativa."""
        if not self.chat_session:
            return "Modo chat não está ativo. Diga 'Stark vamos conversar' para iniciar."

        try:
            # Adicionar histórico de conversa ao contexto para manter memória
            chat_history = ""
            if self.conversation_history:
                # Pegar últimas 5 conversas para contexto
                recent_history = self.conversation_history[-5:]
                chat_history = "\nHistórico da conversa:\n"
                for i, (prev_msg, prev_resp, _) in enumerate(recent_history, 1):
                    chat_history += f"{i}. Usuário: {prev_msg}\n   Stark: {prev_resp}\n"

            full_message = f"{chat_history}\nContexto atual: {context}\n\nMensagem atual: {message}\n\nVocê é Stark, um assistente de voz brasileiro. Mantenha a conversa natural e contextualizada. Sempre em português brasileiro."
            response = self.chat_session.send_message(full_message)
            log_message(f"Mensagem de chat enviada: {message[:50]}...")

            # Adicionar ao histórico de conversas
            self._add_to_conversation_history(message, response.text)

            return response.text
        except Exception as e:
            log_message(f"Erro no chat: {e}", 'error')
            return "Desculpe, houve um erro na conversa."
