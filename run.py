import sys
import os

# Adicionar raiz do projeto e src ao path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from core import StarkCore

def main():
    core = StarkCore()
    core.run()

if __name__ == "__main__":
    main()
