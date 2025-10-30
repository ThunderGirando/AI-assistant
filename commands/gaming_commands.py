from src.gaming_ai import GamingAI
from src.voice import VoiceAssistant
from src.vision import VisionModule
from src.ai_api import AIAPI
from src.learning_mode import LearningMode
from src.utils import log_message

gaming_ai = GamingAI()

def handle_gaming_command(command, voice, vision, ai, learning_mode, LearningMode):
    """Processa comandos relacionados ao Gaming AI."""
    log_message(f"Processando comando de gaming: {command}")

    if 'iniciar aprendizado' in command or 'começar gravar' in command or 'gravar jogo' in command:
        voice.speak("Qual nome você quer dar para esta sessão de aprendizado?")
        session_name = voice.listen()
        if session_name:
            gaming_ai.start_learning_session(session_name.strip())
            voice.speak(f"Sessão de aprendizado '{session_name}' iniciada. Jogue normalmente, eu vou observar suas ações.")
        else:
            voice.speak("Não entendi o nome da sessão.")

    elif 'parar aprendizado' in command or 'parar gravar' in command or 'finalizar gravação' in command:
        gaming_ai.stop_learning_session()
        voice.speak("Sessão de aprendizado finalizada.")

    elif 'jogar sozinho' in command or 'modo autônomo' in command or 'reproduzir jogo' in command:
        sessions = gaming_ai.list_sessions()
        if not sessions:
            voice.speak("Não há sessões gravadas. Primeiro grave uma sessão de aprendizado.")
            return True

        voice.speak(f"Encontrei {len(sessions)} sessões: {', '.join(sessions)}. Qual você quer reproduzir?")
        session_choice = voice.listen()
        if session_choice:
            # Tentar encontrar sessão por nome aproximado
            chosen_session = None
            for session in sessions:
                if session.lower() in session_choice.lower():
                    chosen_session = session
                    break

            if chosen_session:
                voice.speak("Quer ajustar a velocidade? Diga um número ou 'normal'.")
                speed_response = voice.listen()
                speed = 1.0
                if speed_response:
                    try:
                        speed = float(speed_response)
                    except:
                        speed = 1.0

                gaming_ai.start_autonomous_playing(chosen_session, speed)
                voice.speak(f"Iniciando reprodução da sessão '{chosen_session}' com velocidade {speed}x.")
            else:
                voice.speak("Não encontrei essa sessão.")

    elif 'parar jogo' in command or 'parar autônomo' in command:
        gaming_ai.stop_autonomous_playing()
        voice.speak("Jogo autônomo parado.")

    elif 'listar sessões' in command or 'ver gravações' in command:
        sessions = gaming_ai.list_sessions()
        if sessions:
            voice.speak(f"Encontrei {len(sessions)} sessões: {', '.join(sessions)}.")
        else:
            voice.speak("Nenhuma sessão gravada encontrada.")

    elif 'deletar sessão' in command or 'apagar gravação' in command:
        sessions = gaming_ai.list_sessions()
        if not sessions:
            voice.speak("Nenhuma sessão para deletar.")
            return True

        voice.speak(f"Sessões disponíveis: {', '.join(sessions)}. Qual você quer deletar?")
        session_to_delete = voice.listen()
        if session_to_delete:
            deleted = False
            for session in sessions:
                if session.lower() in session_to_delete.lower():
                    if gaming_ai.delete_session(session):
                        voice.speak(f"Sessão '{session}' deletada com sucesso.")
                        deleted = True
                    break

            if not deleted:
                voice.speak("Sessão não encontrada.")

    elif 'status gaming' in command or 'como está' in command:
        status = gaming_ai.get_status()
        if status['is_learning']:
            voice.speak(f"Estou aprendendo. Já capturei {status['actions_recorded']} ações.")
        elif status['is_playing']:
            voice.speak(f"Estou jogando autônomo. Reproduzindo {status['actions_loaded']} ações.")
        else:
            sessions = gaming_ai.list_sessions()
            voice.speak(f"Estou parado. Tenho {len(sessions)} sessões gravadas disponíveis.")

    else:
        return False  # Comando não reconhecido

    return True
