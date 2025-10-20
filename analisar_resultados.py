#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analisar resultados dos experimentos
Extrai informações chave dos logs gerados
"""

import re
import sys

def analisar_arquivo(arquivo):
    """Analisa arquivo de resultados e extrai informações"""

    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo}' não encontrado!")
        print("Execute primeiro: python run_all_experiments.py > resultados_experimentos.txt 2>&1")
        sys.exit(1)

    # Remove códigos ANSI
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    content = ansi_escape.sub('', content)

    print("="*80)
    print("ANÁLISE DE RESULTADOS DOS EXPERIMENTOS")
    print("="*80)

    # Extrai vencedores
    print("\n1. VENCEDORES DE CADA EXPERIMENTO:")
    print("-" * 80)
    vencedores = re.findall(r'>>> VENCEDOR: (\w+)', content)
    for i, vencedor in enumerate(vencedores, 1):
        print(f"   Experimento {i}: {vencedor}")

    # Extrai tipos dos vencedores
    print("\n2. TIPOS DOS VEÍCULOS VENCEDORES:")
    print("-" * 80)
    for i, vencedor in enumerate(vencedores, 1):
        # Busca tipo do vencedor
        pattern = rf'{vencedor}.*?Tipo: (\w+)'
        match = re.search(pattern, content)
        if match:
            tipo = match.group(1)
            print(f"   Experimento {i}: {vencedor} ({tipo})")

    # Extrai prioridades dos vencedores
    print("\n3. PRIORIDADES DOS VENCEDORES:")
    print("-" * 80)
    for i, vencedor in enumerate(vencedores, 1):
        pattern = rf'{vencedor}.*?Prioridade: (\d+)'
        match = re.search(pattern, content)
        if match:
            prio = match.group(1)
            print(f"   Experimento {i}: Prioridade {prio}")

    # Conta total de veículos por experimento
    print("\n4. NÚMERO DE VEÍCULOS POR EXPERIMENTO:")
    print("-" * 80)
    experimentos = re.findall(r'EXPERIMENTO (\d+):.*?Total: (\d+) propostas', content, re.DOTALL)
    for num, total in experimentos:
        print(f"   Experimento {num}: {total} veículos")

    # Status dos experimentos
    print("\n5. STATUS DE EXECUÇÃO:")
    print("-" * 80)
    status_ok = re.findall(r'\[OK\] (.+)', content)
    for experimento in status_ok:
        print(f"   ✓ {experimento}")

    # Estatísticas
    print("\n6. ESTATÍSTICAS:")
    print("-" * 80)
    print(f"   Total de experimentos: {len(vencedores)}")
    print(f"   Experimentos bem-sucedidos: {len(status_ok)}")

    # Verifica se ambulâncias venceram
    ambulancias = [v for v in vencedores if 'Ambulancia' in v]
    print(f"   Vezes que ambulância venceu: {len(ambulancias)}")

    print("\n" + "="*80)
    print("ANÁLISE CONCLUÍDA")
    print("="*80)

if __name__ == "__main__":
    arquivo = "resultados_experimentos.txt"

    if len(sys.argv) > 1:
        arquivo = sys.argv[1]

    analisar_arquivo(arquivo)
