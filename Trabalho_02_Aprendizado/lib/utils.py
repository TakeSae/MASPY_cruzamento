"""
Funções utilitárias do Sistema Multi-Agentes
Contém cores ANSI, funções de formatação e gerenciamento de arquivos.

Extraído de: cruzamento_maspy_learning.py (linhas 10-127)
"""

import os
import signal
import sys
from datetime import datetime


# Handler para Ctrl+C
def signal_handler(sig, frame):
    print("\n\n[INTERROMPIDO PELO USUÁRIO]")
    os._exit(0)

signal.signal(signal.SIGINT, signal_handler)


# Cores ANSI para terminal
class Cores:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Cores
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    AMARELO = '\033[93m'
    AZUL = '\033[94m'
    MAGENTA = '\033[95m'
    CIANO = '\033[96m'
    BRANCO = '\033[97m'

    # Backgrounds
    BG_VERDE = '\033[42m'
    BG_VERMELHO = '\033[41m'
    BG_AZUL = '\033[44m'

def cor(texto, cor_code):
    return f"{cor_code}{texto}{Cores.RESET}"

def titulo(texto):
    return cor(texto, Cores.BOLD + Cores.CIANO)

def sucesso(texto):
    return cor(texto, Cores.VERDE)

def erro(texto):
    return cor(texto, Cores.VERMELHO)

def aviso(texto):
    return cor(texto, Cores.AMARELO)

def info(texto):
    return cor(texto, Cores.CIANO)

def destaque(texto):
    return cor(texto, Cores.BOLD + Cores.BRANCO)


# FUNÇÕES DE ORGANIZAÇÃO DE RESULTADOS POR TIMESTAMP

def criar_diretorio_resultados(nome_experimento="padrao"):
    """
    Cria estrutura de diretórios para salvar resultados com timestamp.
    Similar ao sistema do cruzamento_maspy_v3.

    Estrutura:
        resultados/
            YYYYMMDD_HHMMSS/
                graficos/
                metricas_aprendizado.csv
                info_execucao.txt

    Returns:
        str: Caminho do diretório criado (ex: resultados/20251129_153045)
    """
    # Criar timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Criar estrutura de pastas
    dir_base = "resultados"
    dir_execucao = os.path.join(dir_base, timestamp)
    dir_graficos = os.path.join(dir_execucao, "graficos")

    os.makedirs(dir_graficos, exist_ok=True)

    # Criar arquivo de informações da execução
    info_path = os.path.join(dir_execucao, "info_execucao.txt")
    with open(info_path, 'w') as f:
        f.write(f"Execução do Sistema Multi-Agentes com Q-Learning\n")
        f.write(f"="*60 + "\n\n")
        f.write(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Experimento: {nome_experimento}\n")
        f.write(f"Timestamp: {timestamp}\n")

    print(f"\n{sucesso('✓')} Diretório de resultados criado: {dir_execucao}/")

    # Criar symlink para última execução
    link_ultima = os.path.join(dir_base, "ultima_execucao")
    if os.path.islink(link_ultima) or os.path.exists(link_ultima):
        os.remove(link_ultima)
    os.symlink(timestamp, link_ultima)

    return dir_execucao


def salvar_info_adicional(dir_execucao, info_dict):
    """
    Adiciona informações extras ao arquivo info_execucao.txt.

    Args:
        dir_execucao: Caminho do diretório da execução
        info_dict: Dicionário com informações adicionais
    """
    info_path = os.path.join(dir_execucao, "info_execucao.txt")

    with open(info_path, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("Informações Adicionais:\n")
        f.write("="*60 + "\n\n")

        for chave, valor in info_dict.items():
            f.write(f"{chave}: {valor}\n")
