#!/usr/bin/env python3
"""
Stark AI Assistant - Ponto de entrada principal
"""

import sys
import os

# Adicionar diretório src ao path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from core import StarkCore

def main():
    """Função principal do assistente Stark."""
    try:
        # Inicializar Stark
        stark = StarkCore()

        # Executar loop principal
        stark.run()

    except KeyboardInterrupt:
        print("\nStark AI finalizado pelo usuário.")
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
