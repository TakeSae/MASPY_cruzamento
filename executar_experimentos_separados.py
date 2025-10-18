# -*- coding: utf-8 -*-
"""
Script para executar experimentos em processos separados
Cada experimento roda isoladamente para evitar problemas de estado do MASPY
"""

import subprocess
import sys
import time

def executar_comando(script, experimento):
    """Executa um experimento em processo separado"""
    print(f"\n{'='*80}")
    print(f"Executando Experimento {experimento}...")
    print('='*80)

    try:
        result = subprocess.run(
            [sys.executable, script, str(experimento)],
            capture_output=True,
            text=True,
            timeout=15
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"[OK] Experimento {experimento} concluido com sucesso")
        else:
            print(f"[ERRO] Experimento {experimento} falhou (codigo: {result.returncode})")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Experimento {experimento} excedeu 15 segundos")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao executar experimento {experimento}: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SUITE DE EXPERIMENTOS - EXECUÇÃO ISOLADA")
    print("="*80)

    # Criar script individual de experimento
    script_individual = "d:\\Projects\\MESTRADO\\SMA\\MASPY_cruzamento\\executar_experimento_individual.py"

    experimentos = [
        "Experimento 1: Cenário Base",
        "Experimento 2: Múltiplas Emergências",
        "Experimento 3: Prioridades Iguais",
        "Experimento 4: Cargas Pesadas",
        "Experimento 5: Cenário Misto",
        "Experimento 6: Teste de Estresse"
    ]

    sucessos = 0
    falhas = 0

    for i in range(1, 7):
        print(f"\n>>> {experimentos[i-1]}")
        if executar_comando(script_individual, i):
            sucessos += 1
        else:
            falhas += 1
        time.sleep(1)  # Pausa entre experimentos

    print("\n" + "="*80)
    print("RESUMO DA EXECUÇÃO")
    print("="*80)
    print(f"Sucessos: {sucessos}")
    print(f"Falhas: {falhas}")
    print("="*80)
