import random
import numpy as np
from utils import log_message

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'  # IA é 'O', usuário é 'X'

    def print_board(self):
        """Imprime o tabuleiro."""
        for i in range(0, 9, 3):
            print(f"{self.board[i]} | {self.board[i+1]} | {self.board[i+2]}")
            if i < 6:
                print("-" * 5)

    def check_winner(self):
        """Verifica se há um vencedor."""
        win_conditions = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for condition in win_conditions:
            if self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]] != ' ':
                return self.board[condition[0]]
        if ' ' not in self.board:
            return 'Tie'
        return None

    def make_move(self, position, player):
        """Faz uma jogada."""
        if self.board[position] == ' ':
            self.board[position] = player
            return True
        return False

    def ai_move(self):
        """IA faz uma jogada simples (aleatória, pode ser melhorada com RL)."""
        available_moves = [i for i in range(9) if self.board[i] == ' ']
        if available_moves:
            move = random.choice(available_moves)
            self.make_move(move, 'O')
            log_message(f"IA jogou na posição: {move}")
            return move
        return None

    def play_game(self, voice_assistant):
        """Joga uma partida contra o usuário."""
        voice_assistant.speak("Vamos jogar jogo da velha! Você é X, eu sou O. Diga a posição de 1 a 9.")
        while True:
            self.print_board()
            winner = self.check_winner()
            if winner:
                if winner == 'Tie':
                    voice_assistant.speak("Empate!")
                else:
                    voice_assistant.speak(f"{winner} venceu!")
                break

            if self.current_player == 'X':
                voice_assistant.speak("Sua vez. Qual posição?")
                position = voice_assistant.listen()
                if position:
                    try:
                        pos = int(position) - 1
                        if 0 <= pos < 9 and self.make_move(pos, 'X'):
                            self.current_player = 'O'
                        else:
                            voice_assistant.speak("Posição inválida. Tente novamente.")
                    except ValueError:
                        voice_assistant.speak("Por favor, diga um número de 1 a 9.")
                else:
                    voice_assistant.speak("Não entendi. Tente novamente.")
            else:
                move = self.ai_move()
                if move is not None:
                    voice_assistant.speak(f"Joguei na posição {move + 1}.")
                    self.current_player = 'X'
                else:
                    voice_assistant.speak("Erro na jogada da IA.")

class GameModule:
    def __init__(self):
        self.games = {
            'tic_tac_toe': TicTacToe
        }

    def start_game(self, game_name, voice_assistant):
        """Inicia um jogo."""
        if game_name in self.games:
            game = self.games[game_name]()
            game.play_game(voice_assistant)
        else:
            voice_assistant.speak("Jogo não encontrado.")
