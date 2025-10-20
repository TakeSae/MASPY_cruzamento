#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para executar todos os experimentos sequencialmente
Cada experimento roda em um processo Python separado para evitar conflitos
"""

import subprocess
import sys

def run_experiment(name, func_name):
    """Executa um experimento individual"""
    print(f"\nExecutando {name}...")
    cmd = f"python -c 'from experimentos_cruzamento import {func_name}; {func_name}()'"

    try:
        result = subprocess.run(cmd, shell=True, check=True, timeout=10)
        print(f"  {name} concluido com sucesso!")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ERRO: {name} excedeu o tempo limite!")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ERRO ao executar {name}: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("SUITE DE EXPERIMENTOS - SISTEMA DE NEGOCIACAO EM CRUZAMENTO")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*80)
    print("\nExecutando 6 experimentos separadamente...")

    experimentos = [
        ("Experimento 1 - Cenario Base", "experimento_1_base"),
        ("Experimento 2 - Multiplas Emergencias", "experimento_2_multiplas_emergencias"),
        ("Experimento 3 - Prioridades Iguais", "experimento_3_prioridades_iguais"),
        ("Experimento 4 - Cargas Pesadas", "experimento_4_cargas_pesadas"),
        ("Experimento 5 - Cenario Misto", "experimento_5_misto"),
        ("Experimento 6 - Teste de Estresse", "experimento_6_estresse"),
    ]

    resultados = []
    for nome, func in experimentos:
        sucesso = run_experiment(nome, func)
        resultados.append((nome, sucesso))

    print("\n" + "="*80)
    print("RESUMO DA EXECUCAO")
    print("="*80)

    for nome, sucesso in resultados:
        status = "OK" if sucesso else "FALHOU"
        print(f"  [{status}] {nome}")

    total_sucesso = sum(1 for _, s in resultados if s)

    print("\n" + "="*80)
    if total_sucesso == len(experimentos):
        print("TODOS OS EXPERIMENTOS CONCLUIDOS COM SUCESSO!")
        sys.exit(0)
    else:
        print(f"ALGUNS EXPERIMENTOS FALHARAM: {total_sucesso}/{len(experimentos)} concluidos")
        sys.exit(1)

    print("="*80)
