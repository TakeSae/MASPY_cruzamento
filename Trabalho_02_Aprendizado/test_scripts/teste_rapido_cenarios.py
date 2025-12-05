#!/usr/bin/env python3
"""
Script para teste rápido de 2 cenários (extremos e base).
Útil para verificar se o sistema está funcionando antes de executar todos os 30 testes.

Sistemas Multiagentes - 2025.2 - UTFPR
Trabalho 02 - Aprendizado por Reforço
Autores: Guilherme T. S. Abreu, Maria Eduarda S. Freitas
"""

import subprocess
import sys
import os
import time

# Detectar ambiente virtual MASPY
def find_venv_python():
    """Encontra o executável Python do ambiente virtual MASPY."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(script_dir, "..", "venv_maspy", "bin", "python"),
        os.path.join(script_dir, "..", "venv_maspy", "bin", "python3"),
        "/home/dachii/Projetos/MESTRADO/MASPY_cruzamento/venv_maspy/bin/python",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)

    print("AVISO: Ambiente virtual MASPY não encontrado.")
    return sys.executable

PYTHON_EXECUTABLE = find_venv_python()

# Apenas 2 cenários simples para teste rápido
CENARIOS_TESTE = ["extremos", "base"]
EPISODIOS = 20  # Poucos episódios para teste rápido

def executar_cenario(cenario):
    """Executa um cenário de teste."""
    print(f"\n{'='*60}")
    print(f"Executando: {cenario} com {EPISODIOS} episódios")
    print(f"{'='*60}\n")

    cmd = [
        PYTHON_EXECUTABLE,
        "cruzamento_maspy_learning.py",
        "--experimento", cenario,
        "--episodios", str(EPISODIOS),
        "--quiet"
    ]

    inicio = time.time()
    try:
        processo = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        saida, _ = processo.communicate(input="\n")
        tempo_total = time.time() - inicio

        if processo.returncode == 0:
            print(f"OK - Concluído em {tempo_total:.1f}s")
            return True
        else:
            print(f"ERRO após {tempo_total:.1f}s")
            print(saida[-500:])  # Últimas 500 chars
            return False

    except Exception as e:
        print(f"EXCEÇÃO: {e}")
        return False


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║  TESTE RÁPIDO - 2 Cenários                               ║
║  Sistema Multi-Agentes com Q-Learning                    ║
╚══════════════════════════════════════════════════════════╝
    """)

    print(f"Python: {PYTHON_EXECUTABLE}")
    print(f"Cenários: {CENARIOS_TESTE}")
    print(f"Episódios por cenário: {EPISODIOS}")

    inicio_total = time.time()
    sucessos = 0

    for cenario in CENARIOS_TESTE:
        if executar_cenario(cenario):
            sucessos += 1

    tempo_total = time.time() - inicio_total

    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL")
    print(f"{'='*60}")
    print(f"Sucessos: {sucessos}/{len(CENARIOS_TESTE)}")
    print(f"Tempo total: {tempo_total:.1f}s")
    print(f"{'='*60}\n")

    if sucessos == len(CENARIOS_TESTE):
        print("SUCESSO! Sistema está funcionando corretamente.")
        print("Para executar todos os cenários, use: python executar_todos_cenarios.py")
    else:
        print("FALHA! Verifique os erros acima.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecução cancelada pelo usuário")
        sys.exit(1)
