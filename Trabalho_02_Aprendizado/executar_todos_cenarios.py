#!/usr/bin/env python3
"""
Script para executar todos os cenários automaticamente.
Gera tabelas comparativas e análises entre diferentes configurações.

Sistemas Multiagentes - 2025.2 - UTFPR
Trabalho 02 - Aprendizado por Reforço
Autores: Guilherme T. S. Abreu, Maria Eduarda S. Freitas
"""

import subprocess
import sys
import os
import csv
import time
from pathlib import Path

# Detectar ambiente virtual MASPY
def find_venv_python():
    """Encontra o executável Python do ambiente virtual MASPY."""
    # Caminho correto do venv a partir do diretório Trabalho_02_Aprendizado
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Tentar vários caminhos possíveis
    possible_paths = [
        os.path.join(script_dir, "..", "venv_maspy", "bin", "python"),
        os.path.join(script_dir, "..", "venv_maspy", "bin", "python3"),
        "/home/dachii/Projetos/MESTRADO/MASPY_cruzamento/venv_maspy/bin/python",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            abs_path = os.path.abspath(path)
            return abs_path

    # Se não encontrou, usar o Python atual (pode não ter MASPY)
    print("AVISO: Ambiente virtual MASPY não encontrado. Usando Python do sistema.")
    print("Se houver erros, ative o ambiente virtual manualmente:")
    print("  source ../venv_maspy/bin/activate")
    return sys.executable

PYTHON_EXECUTABLE = find_venv_python()
print(f"Usando Python: {PYTHON_EXECUTABLE}\n")

# Configurações de execução
CENARIOS = [
    "padrao",
    "base",
    "emergencias",
    "iguais",
    "pesados",
    "transporte_publico",
    "prioridades_proximas",
    "extremos",
    "escalonado",
    "misto_complexo"
]

EPISODIOS_CONFIGS = [50, 100, 200]  # Diferentes números de episódios

def executar_cenario(cenario, episodios):
    """
    Executa um cenário específico com número de episódios dado.

    Args:
        cenario: Nome do cenário
        episodios: Número de episódios

    Returns:
        (sucesso, tempo_execucao, diretorio_resultado)
    """
    print(f"\n{'='*70}")
    print(f"Executando: {cenario} com {episodios} episódios")
    print(f"{'='*70}\n")

    cmd = [
        PYTHON_EXECUTABLE,
        "cruzamento_maspy_learning.py",
        "--experimento", cenario,
        "--episodios", str(episodios),
        "--quiet"
    ]

    inicio = time.time()
    try:
        # Executar com echo "" para auto-pressionar ENTER
        processo = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # Enviar ENTER automaticamente
        saida, _ = processo.communicate(input="\n")

        tempo_total = time.time() - inicio

        if processo.returncode == 0:
            # Extrair diretório de resultados da saída
            for linha in saida.split('\n'):
                if 'resultados/' in linha and 'Diretório de resultados criado' in linha:
                    # Exemplo: "Diretório de resultados criado: resultados/20251204_130354/"
                    diretorio = linha.split('resultados/')[1].split('/')[0]
                    return True, tempo_total, f"resultados/{diretorio}"

            # Se não encontrou, procurar symlink última_execução
            return True, tempo_total, "resultados/ultima_execucao"
        else:
            print(f"Erro ao executar {cenario}")
            print(saida)
            return False, tempo_total, None

    except Exception as e:
        print(f"Exceção ao executar {cenario}: {e}")
        return False, time.time() - inicio, None


def coletar_metricas(diretorio):
    """
    Coleta métricas de uma execução.

    Args:
        diretorio: Diretório dos resultados

    Returns:
        dict com métricas coletadas
    """
    info_path = Path(diretorio) / "info_execucao.txt"
    csv_path = Path(diretorio) / "metricas_aprendizado.csv"

    metricas = {}

    # Ler info_execucao.txt
    if info_path.exists():
        with open(info_path, 'r') as f:
            for linha in f:
                if ':' in linha:
                    chave, valor = linha.split(':', 1)
                    chave = chave.strip()
                    valor = valor.strip()

                    if chave == "Experimento":
                        metricas['experimento'] = valor
                    elif chave == "Número de episódios":
                        metricas['episodios'] = int(valor)
                    elif chave == "Número de veículos":
                        metricas['num_veiculos'] = int(valor)
                    elif chave == "Tempo total de execução (s)":
                        metricas['tempo_execucao'] = float(valor)
                    elif chave == "Recompensa por escolha correta":
                        metricas['recompensa_correta'] = int(valor)

    # Ler metricas_aprendizado.csv
    if csv_path.exists():
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            recompensas = []
            for linha in reader:
                recompensas.append(float(linha['Recompensa']))

            if recompensas:
                metricas['recompensa_media'] = sum(recompensas) / len(recompensas)
                metricas['recompensa_total'] = sum(recompensas)
                metricas['recompensa_min'] = min(recompensas)
                metricas['recompensa_max'] = max(recompensas)

    return metricas


def gerar_tabela_comparativa(resultados, arquivo_saida="comparacao_cenarios.csv"):
    """
    Gera tabela comparativa com todos os resultados.

    Args:
        resultados: Lista de dicts com métricas
        arquivo_saida: Arquivo CSV de saída
    """
    if not resultados:
        print("Nenhum resultado para gerar tabela")
        return

    print(f"\n{'='*70}")
    print(f"Gerando tabela comparativa: {arquivo_saida}")
    print(f"{'='*70}\n")

    with open(arquivo_saida, 'w', newline='') as f:
        campos = [
            'experimento', 'episodios', 'num_veiculos',
            'tempo_execucao', 'recompensa_media', 'recompensa_total',
            'recompensa_min', 'recompensa_max', 'recompensa_correta'
        ]

        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()

        for resultado in resultados:
            writer.writerow(resultado)

    print(f"Tabela salva em: {arquivo_saida}")


def imprimir_resumo(resultados):
    """Imprime resumo dos resultados no terminal."""
    print(f"\n{'='*70}")
    print(f"RESUMO DOS RESULTADOS")
    print(f"{'='*70}\n")

    print(f"{'Cenário':<25} {'Episódios':<10} {'Tempo (s)':<12} {'Recomp. Média':<15}")
    print(f"{'-'*70}")

    for r in resultados:
        print(f"{r['experimento']:<25} {r['episodios']:<10} "
              f"{r.get('tempo_execucao', 0):<12.2f} "
              f"{r.get('recompensa_media', 0):<15.1f}")

    print(f"\n{'='*70}")
    print(f"Total de execuções: {len(resultados)}")
    print(f"{'='*70}\n")


def main():
    """Função principal."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║  EXECUÇÃO AUTOMÁTICA DE TODOS OS CENÁRIOS                         ║
║  Sistema Multi-Agentes com Q-Learning                             ║
║  Trabalho 02 - SMA 2025.2 - UTFPR                                 ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    resultados = []
    total_execucoes = len(CENARIOS) * len(EPISODIOS_CONFIGS)
    execucao_atual = 0

    print(f"Total de execuções planejadas: {total_execucoes}")
    print(f"Cenários: {len(CENARIOS)}")
    print(f"Configurações de episódios: {EPISODIOS_CONFIGS}")
    print(f"\nIniciando execuções...\n")

    inicio_total = time.time()

    for cenario in CENARIOS:
        for episodios in EPISODIOS_CONFIGS:
            execucao_atual += 1

            print(f"\n[{execucao_atual}/{total_execucoes}] {cenario} - {episodios} episódios")

            sucesso, tempo, diretorio = executar_cenario(cenario, episodios)

            if sucesso and diretorio:
                metricas = coletar_metricas(diretorio)
                resultados.append(metricas)
                print(f"Concluído em {tempo:.2f}s")
            else:
                print(f"Falhou após {tempo:.2f}s")

    tempo_total = time.time() - inicio_total

    # Gerar outputs
    gerar_tabela_comparativa(resultados)
    imprimir_resumo(resultados)

    print(f"\n{'='*70}")
    print(f"EXECUÇÃO COMPLETA")
    print(f"{'='*70}")
    print(f"Tempo total: {tempo_total/60:.1f} minutos ({tempo_total:.1f}s)")
    print(f"Execuções bem-sucedidas: {len(resultados)}/{total_execucoes}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecução cancelada pelo usuário")
        sys.exit(1)
