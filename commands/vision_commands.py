"""
Comandos relacionados à visão e observação da tela
"""
import re
import cv2
import time
import sys
sys.path.append('../src')
from utils import log_message

def handle_vision_command(command, voice, vision, learning_mode, LearningMode, ai):
    """Processa comandos relacionados à visão."""
    if 'ver tela' in command or 'o que você vê' in command or 'descreva tela' in command or 'o que está vendo' in command:
        context = vision.get_screen_context()
        voice.speak(f"Estou vendo: {context}")
        return True

    elif 'o que você está observando' in command or 'relatório visual' in command or 'status visual' in command:
        if learning_mode and learning_mode.is_learning:
            observations = learning_mode.observations[-5:] if len(learning_mode.observations) > 5 else learning_mode.observations
            if observations:
                latest_obs = observations[-1]['context']
                voice.speak(f"Estou observando ativamente. Última captura: {latest_obs}. Total de observações: {len(observations)}.")
            else:
                voice.speak("Modo de aprendizado ativo, mas ainda não fiz observações.")
        else:
            context = vision.get_screen_context()
            voice.speak(f"Não estou em modo de aprendizado ativo. Contexto atual: {context}")
        return True

    elif 'veja minha tela' in command or 'ver minha tela' in command or 'veja tela' in command or 'ver tela' in command or 'analise' in command or 'analisar' in command:
        # Comando para ativar observação prioritária do monitor 1
        if not learning_mode:
            learning_mode = LearningMode(voice, vision, ai)
        if not learning_mode.is_learning:
            learning_mode.start_learning()
            learning_mode.specific_monitor = 1  # Priorizar monitor 1
            voice.speak("Ativando observação da tela principal. Vou focar no monitor 1 e aprender com suas ações.")
        else:
            learning_mode.specific_monitor = 1  # Mudar para monitor 1
            voice.speak("Focando observação no monitor 1.")
        return True

    elif 'veja monitor' in command or 'veja tela do monitor' in command:
        # Comando específico para monitor
        monitor_match = re.search(r'monitor\s*(\d+)', command)
        if monitor_match:
            monitor_num = int(monitor_match.group(1))
            if not learning_mode:
                learning_mode = LearningMode(voice, vision, ai)
            if not learning_mode.is_learning:
                learning_mode.start_learning()
                learning_mode.specific_monitor = monitor_num
                voice.speak(f"Ativando observação específica do monitor {monitor_num}. Vou focar apenas neste monitor.")
            else:
                learning_mode.specific_monitor = monitor_num
                voice.speak(f"Mudando foco para o monitor {monitor_num}.")
        else:
            voice.speak("Qual monitor você quer que eu observe? Diga 'veja monitor 1' ou 'veja monitor 2', por exemplo.")
        return True

    elif 'veja todos os monitores' in command or 'veja todas as telas' in command:
        # Comando para observar todos os monitores
        if not learning_mode:
            learning_mode = LearningMode(voice, vision, ai)
        if not learning_mode.is_learning:
            learning_mode.start_learning()
            learning_mode.specific_monitor = None  # None significa todos
            voice.speak("Ativando observação de todos os monitores disponíveis.")
        else:
            learning_mode.specific_monitor = None
            voice.speak("Observando todos os monitores novamente.")
        return True

    elif 'mostrar captura' in command or 'preview tela' in command or 'ver captura' in command or 'tirar foto' in command or 'capturar tela' in command:
        # Comando para mostrar uma preview da captura atual
        try:
            frame = vision.capture_screen()
            if frame.size > 0:
                # Salvar imagem temporária
                import os
                temp_dir = os.path.join(os.getcwd(), 'temp')
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = time.strftime("%H-%M-%S")
                image_path = os.path.join(temp_dir, f'screen_capture_{timestamp}.png')
                cv2.imwrite(image_path, frame)
                voice.speak(f"Captura salva! Arquivo: screen_capture_{timestamp}.png na pasta temp")
                print(f"📸 Captura de tela salva: {image_path}")
                print(f"📐 Dimensões: {frame.shape[1]}x{frame.shape[0]} pixels")
                print(f"🎯 Método usado: {'dxcam (otimizado)' if vision.camera is not None else 'pyautogui (fallback)'}")
            else:
                voice.speak("Não foi possível capturar a tela.")
        except Exception as e:
            voice.speak("Erro ao fazer captura da tela.")
            log_message(f"Erro na preview: {e}", 'error')
        return True

    return False
