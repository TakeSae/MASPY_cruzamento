from maspy import *
import time
import sys
import os

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from MASPY_learning.cruzamento_maspy_gui import (
    VeiculoAgent,
    CoordenadorAgent,
    CruzamentoEnvironment,
    LogLevel,
    GLOBAL_LOG_LEVEL
)

EXPERIMENT_LOG_LEVEL = LogLevel.INFO



# FUNÇÕES AUXILIARES

def criar_sistema(veiculos_config, log_level=None):
    if log_level is None:
        log_level = EXPERIMENT_LOG_LEVEL

    num_veiculos = len(veiculos_config)

    coord = CoordenadorAgent("Coordenador",
                            num_veiculos=num_veiculos,
                            log_level=log_level)

    veiculos = []
    for cfg in veiculos_config:
        v = VeiculoAgent(cfg['nome'],
                        tipo=cfg['tipo'],
                        prioridade=cfg['prio'],
                        coordenador="Coordenador",
                        log_level=log_level)
        veiculos.append(v)

    env = CruzamentoEnvironment()

    return coord, veiculos, env

def executar_experimento(titulo, descricao, veiculos_config, esperado):

    print("\n" + "="*80)
    print(f"EXPERIMENTO: {titulo}")
    print("="*80)
    print(f"\n{descricao}")
    print(f"Resultado esperado: {esperado}\n")

    print("Veículos participantes:")
    for v in veiculos_config:
        print(f"  - {v['nome']}: {v['tipo']} (prioridade={v['prio']})")

    print("\nIniciando negociação...\n")
    print("-" * 80 + "\n")

    coord, veiculos, env = criar_sistema(veiculos_config)

    agentes = [coord] + veiculos
    Admin().connect_to(agentes, env)

    inicio = time.time()
    Admin().start_system()
    fim = time.time()

    print("\n" + "-" * 80)
    print(f"EXPERIMENTO CONCLUÍDO (Tempo: {fim-inicio:.3f}s)")
    print("="*80 + "\n")




# EXPERIMENTOS

def experimento_1_base():

    titulo = "1: Cenário Base"
    descricao = "Ambulância deve vencer contra veículos normais"
    esperado = "Ambulância (prioridade 100)"

    veiculos = [
        {'nome': 'Carro1', 'tipo': 'carro', 'prio': 10},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prio': 100},
        {'nome': 'Moto1', 'tipo': 'moto', 'prio': 5},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prio': 30},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)

def experimento_2_multiplas_emergencias():

    titulo = "2: Múltiplas Emergências"
    descricao = "Ambulância1 (prio=100) deve vencer"
    esperado = "Ambulância1 (maior prioridade)"

    veiculos = [
        {'nome': 'Ambulancia1', 'tipo': 'ambulancia', 'prio': 100},
        {'nome': 'Ambulancia2', 'tipo': 'ambulancia', 'prio': 95},
        {'nome': 'Bombeiros', 'tipo': 'bombeiros', 'prio': 98},
        {'nome': 'Carro1', 'tipo': 'carro', 'prio': 10},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)

def experimento_3_prioridades_iguais():

    titulo = "3: Prioridades Iguais"
    descricao = "Primeiro a ser processado vence"
    esperado = "Qualquer Carro (ordem de processamento)"

    veiculos = [
        {'nome': 'Carro1', 'tipo': 'carro', 'prio': 10},
        {'nome': 'Carro2', 'tipo': 'carro', 'prio': 10},
        {'nome': 'Carro3', 'tipo': 'carro', 'prio': 10},
        {'nome': 'Carro4', 'tipo': 'carro', 'prio': 10},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)

def experimento_4_cargas_pesadas():

    titulo = "4: Cargas Pesadas"
    descricao = "Caminhão (prio=50) deve vencer"
    esperado = "Caminhão (maior prioridade)"

    veiculos = [
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prio': 50},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prio': 40},
        {'nome': 'Moto1', 'tipo': 'moto', 'prio': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prio': 10},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)

def experimento_5_misto():

    titulo = "5: Cenário Misto (6 veículos)"
    descricao = "Ambulância deve vencer entre 6 veículos diferentes"
    esperado = "Ambulância (maior prioridade)"

    veiculos = [
        {'nome': 'Moto1', 'tipo': 'moto', 'prio': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prio': 15},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prio': 35},
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prio': 45},
        {'nome': 'Taxi1', 'tipo': 'taxi', 'prio': 20},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prio': 100},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)

def experimento_6_estresse():

    titulo = "6: Teste de Estresse (10 veículos)"
    descricao = "Veículo10 (prio=100) deve vencer"
    esperado = "Veículo10 (maior prioridade)"

    veiculos = [
        {'nome': 'Veiculo1', 'tipo': 'veiculo', 'prio': 10},
        {'nome': 'Veiculo2', 'tipo': 'veiculo', 'prio': 20},
        {'nome': 'Veiculo3', 'tipo': 'veiculo', 'prio': 30},
        {'nome': 'Veiculo4', 'tipo': 'veiculo', 'prio': 40},
        {'nome': 'Veiculo5', 'tipo': 'veiculo', 'prio': 50},
        {'nome': 'Veiculo6', 'tipo': 'veiculo', 'prio': 60},
        {'nome': 'Veiculo7', 'tipo': 'veiculo', 'prio': 70},
        {'nome': 'Veiculo8', 'tipo': 'veiculo', 'prio': 80},
        {'nome': 'Veiculo9', 'tipo': 'veiculo', 'prio': 90},
        {'nome': 'Veiculo10', 'tipo': 'veiculo', 'prio': 100},
    ]

    executar_experimento(titulo, descricao, veiculos, esperado)




# EXECUÇÃO COM SUBPROCESS (evita problemas do MASPY)

import subprocess
import sys

def run_experiment(name, func_name):

    print(f"\n[{time.strftime('%H:%M:%S')}] Executando {name}...")

    cmd = f"python -c 'from experimentos_cruzamento_v3 import {func_name}; {func_name}()'"

    try:
        inicio = time.time()
        result = subprocess.run(cmd, shell=True, check=True, timeout=15)
        fim = time.time()
        print(f"    {name} concluído! (Tempo: {fim-inicio:.3f}s)")
        return True, fim-inicio
    except subprocess.TimeoutExpired:
        print(f"     ERRO: {name} excedeu tempo limite!")
        return False, 0
    except subprocess.CalledProcessError as e:
        print(f"     ERRO ao executar {name}: {e}")
        return False, 0




# EXECUÇÃO PRINCIPAL

if __name__ == "__main__":
    print("="*80)
    print("SUITE DE EXPERIMENTOS - SISTEMA DE NEGOCIAÇÃO EM CRUZAMENTO v3")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*80)
    print(f"\nNível de log: {EXPERIMENT_LOG_LEVEL.name}")
    print("Executando 6 experimentos separadamente (subprocess)...\n")

    inicio_total = time.time()

    experimentos = [
        ("Experimento 1 - Cenário Base", "experimento_1_base"),
        ("Experimento 2 - Múltiplas Emergências", "experimento_2_multiplas_emergencias"),
        ("Experimento 3 - Prioridades Iguais", "experimento_3_prioridades_iguais"),
        ("Experimento 4 - Cargas Pesadas", "experimento_4_cargas_pesadas"),
        ("Experimento 5 - Cenário Misto", "experimento_5_misto"),
        ("Experimento 6 - Teste de Estresse", "experimento_6_estresse"),
    ]

    resultados = []
    for nome, func in experimentos:
        sucesso, tempo = run_experiment(nome, func)
        resultados.append((nome, sucesso, tempo))

    fim_total = time.time()

    print("\n" + "="*80)
    print("RESUMO DA EXECUÇÃO")
    print("="*80)

    for nome, sucesso, tempo in resultados:
        status = "OK" if sucesso else "FALHOU"
        tempo_str = f"{tempo:.3f}s" if tempo > 0 else "N/A"
        print(f"  [{status}] {nome} - {tempo_str}")

    total_sucesso = sum(1 for _, s, _ in resultados if s)

    print("\n" + "="*80)
    print(f"Tempo total: {fim_total - inicio_total:.3f}s")
    print("="*80)

    if total_sucesso == len(experimentos):
        print("TODOS OS EXPERIMENTOS CONCLUÍDOS COM SUCESSO!")
        sys.exit(0)
    else:
        print(f"ALGUNS EXPERIMENTOS FALHARAM: {total_sucesso}/{len(experimentos)} concluídos")
        sys.exit(1)
