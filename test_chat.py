#!/usr/bin/env python3
"""
Script de teste para o modo chat multi-turn do Stark AI.
Permite testar conversas via texto sem precisar usar voz.
"""

import sys
import os

# Adicionar diretório src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from core import StarkCore

def test_chat_mode():
    """Testa o modo chat multi-turn via entrada de texto."""
    print("=== TESTE DO MODO CHAT MULTI-TURN ===")
    print("Digite comandos como se estivesse falando com o Stark.")
    print("Para sair, digite 'sair' ou pressione Ctrl+C")
    print()

    # Inicializar StarkCore (sem voz)
    stark = StarkCore()

    # Simular entrada inicial
    print("🤖 Sistema STARK iniciado. Diga 'STARK' para me chamar.")
    print()

    while True:
        try:
            # Receber entrada do usuário
            user_input = input("👤 Você: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break

            # Simular processamento do comando
            print("🎯 Processando comando...")

            try:
                # Verificar se é comando local primeiro
                if stark._try_local_commands(user_input):
                    print("✅ Comando local processado")
                else:
                    # Fallback para AI
                    stark._fallback_to_ai(user_input)
                    print("🤖 Resposta da IA processada")
            except Exception as e:
                print(f"❌ Erro ao processar comando: {e}")

            print("-" * 50)
            print("💡 Digite sua próxima pergunta ou 'sair' para encerrar:")

        except KeyboardInterrupt:
            print("\n👋 Teste interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            break

if __name__ == "__main__":
    test_chat_mode()
