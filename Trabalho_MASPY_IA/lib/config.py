"""
Configurações do Sistema Multi-Agentes com Q-Learning
Contém configurações de veículos, cenários e níveis de log.

Extraído de: cruzamento_maspy_learning.py (linhas 131-325)
"""

from enum import Enum


# SISTEMA DE LOG LEVELS

class LogLevel(Enum):
    SILENT = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

GLOBAL_LOG_LEVEL = LogLevel.INFO



# CONFIGURAÇÃO DOS VEÍCULOS

VEICULOS_CONFIG = [
    {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
    {"nome": "Bombeiros", "tipo": "bombeiros", "prioridade": 98},
    {"nome": "Policia", "tipo": "policia", "prioridade": 95},
    {"nome": "Caminhao", "tipo": "caminhao", "prioridade": 50},
    {"nome": "Onibus", "tipo": "onibus", "prioridade": 40},
    {"nome": "Taxi", "tipo": "taxi", "prioridade": 25},
    {"nome": "Carro1", "tipo": "carro", "prioridade": 15},
    {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
    {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
    {"nome": "Moto2", "tipo": "moto", "prioridade": 3},
]

# CONFIGURAÇÕES DE EXPERIMENTOS

EXPERIMENTOS = {
    "base-novo": {
        "titulo": "Cenário Base (16 veículos)",
        "descricao": "Ambulância deve vencer contra veículos normais",
        "veiculos": [
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro3", "tipo": "carro", "prioridade": 10},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto2", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto3", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto4", "tipo": "moto", "prioridade": 5},
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
        ]
    },
    "padrao": {
        "titulo": "Cenário Padrão (10 veículos)",
        "descricao": "10 veículos com prioridades diferentes - teste completo",
        "veiculos": VEICULOS_CONFIG
    },
    "base": {
        "titulo": "Cenário Base (10 veículos)",
        "descricao": "Ambulância deve vencer contra veículos normais",
        "veiculos": [
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro3", "tipo": "carro", "prioridade": 10},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto2", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto3", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto4", "tipo": "moto", "prioridade": 5},
        ]
    },
    "emergencias": {
        "titulo": "Múltiplas Emergências (10 veículos)",
        "descricao": "Ambulância1 (prio=100) deve vencer entre emergências",
        "veiculos": [
            {"nome": "Ambulancia1", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Bombeiros", "tipo": "bombeiros", "prioridade": 98},
            {"nome": "Ambulancia2", "tipo": "ambulancia", "prioridade": 95},
            {"nome": "Policia", "tipo": "policia", "prioridade": 93},
            {"nome": "Caminhao1", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
        ]
    },
    "iguais": {
        "titulo": "Prioridades Iguais (10 veículos)",
        "descricao": "Todos com mesma prioridade - ordem de processamento",
        "veiculos": [
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro3", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro4", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro5", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro6", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro7", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro8", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro9", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro10", "tipo": "carro", "prioridade": 10},
        ]
    },
    "pesados": {
        "titulo": "Cargas Pesadas (10 veículos)",
        "descricao": "Caminhão (prio=50) deve vencer",
        "veiculos": [
            {"nome": "Caminhao1", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Caminhao2", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Onibus2", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto2", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto3", "tipo": "moto", "prioridade": 5},
        ]
    },
    "transporte_publico": {
        "titulo": "Transporte Público (10 veículos)",
        "descricao": "Ônibus vs Táxi vs veículos particulares",
        "veiculos": [
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Onibus2", "tipo": "onibus", "prioridade": 40},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Taxi2", "tipo": "taxi", "prioridade": 25},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro3", "tipo": "carro", "prioridade": 10},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto2", "tipo": "moto", "prioridade": 5},
            {"nome": "Moto3", "tipo": "moto", "prioridade": 5},
        ]
    },
    "prioridades_proximas": {
        "titulo": "Prioridades Próximas (10 veículos)",
        "descricao": "Diferenças pequenas de prioridade (desafio para Q-Learning)",
        "veiculos": [
            {"nome": "Veiculo1", "tipo": "carro", "prioridade": 55},
            {"nome": "Veiculo2", "tipo": "carro", "prioridade": 53},
            {"nome": "Veiculo3", "tipo": "carro", "prioridade": 51},
            {"nome": "Veiculo4", "tipo": "carro", "prioridade": 49},
            {"nome": "Veiculo5", "tipo": "carro", "prioridade": 47},
            {"nome": "Veiculo6", "tipo": "carro", "prioridade": 45},
            {"nome": "Veiculo7", "tipo": "carro", "prioridade": 43},
            {"nome": "Veiculo8", "tipo": "carro", "prioridade": 41},
            {"nome": "Veiculo9", "tipo": "carro", "prioridade": 39},
            {"nome": "Veiculo10", "tipo": "carro", "prioridade": 37},
        ]
    },
    "extremos": {
        "titulo": "Prioridades Extremas (10 veículos)",
        "descricao": "Grande diferença entre prioridades (1 vs 100)",
        "veiculos": [
            {"nome": "Emergencia1", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Emergencia2", "tipo": "bombeiros", "prioridade": 98},
            {"nome": "Importante1", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Importante2", "tipo": "onibus", "prioridade": 40},
            {"nome": "Normal1", "tipo": "taxi", "prioridade": 25},
            {"nome": "Normal2", "tipo": "carro", "prioridade": 10},
            {"nome": "Normal3", "tipo": "carro", "prioridade": 10},
            {"nome": "Baixa1", "tipo": "moto", "prioridade": 5},
            {"nome": "Baixa2", "tipo": "moto", "prioridade": 3},
            {"nome": "Baixa3", "tipo": "moto", "prioridade": 1},
        ]
    },
    "escalonado": {
        "titulo": "Prioridades Escalonadas (10 veículos)",
        "descricao": "Escala uniforme de 10 até 100 de 10 em 10",
        "veiculos": [
            {"nome": "V100", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "V90", "tipo": "bombeiros", "prioridade": 90},
            {"nome": "V80", "tipo": "policia", "prioridade": 80},
            {"nome": "V70", "tipo": "caminhao", "prioridade": 70},
            {"nome": "V60", "tipo": "caminhao", "prioridade": 60},
            {"nome": "V50", "tipo": "onibus", "prioridade": 50},
            {"nome": "V40", "tipo": "onibus", "prioridade": 40},
            {"nome": "V30", "tipo": "taxi", "prioridade": 30},
            {"nome": "V20", "tipo": "carro", "prioridade": 20},
            {"nome": "V10", "tipo": "moto", "prioridade": 10},
        ]
    },
    "misto_complexo": {
        "titulo": "Cenário Misto Complexo (10 veículos)",
        "descricao": "Mix de todos os tipos com prioridades variadas",
        "veiculos": [
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Caminhao_Carga", "tipo": "caminhao", "prioridade": 55},
            {"nome": "Onibus_Escolar", "tipo": "onibus", "prioridade": 45},
            {"nome": "Policia_Patrulha", "tipo": "policia", "prioridade": 92},
            {"nome": "Taxi_Corrida", "tipo": "taxi", "prioridade": 20},
            {"nome": "Carro_Executivo", "tipo": "carro", "prioridade": 35},
            {"nome": "Moto_Entrega", "tipo": "moto", "prioridade": 15},
            {"nome": "Caminhao_Lixo", "tipo": "caminhao", "prioridade": 30},
            {"nome": "Carro_Particular", "tipo": "carro", "prioridade": 8},
            {"nome": "Bombeiros_Resgate", "tipo": "bombeiros", "prioridade": 99},
        ]
    },
    "dois_veiculos": {
        "titulo": "Cenário Mínimo",
        "descricao": "Apenas 2 veículos - caso mais simples",
        "veiculos": [
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Carro", "tipo": "carro", "prioridade": 10},
        ]
    },
    "tres_veiculos": {
        "titulo": "Três Veículos",
        "descricao": "3 veículos com prioridades distintas",
        "veiculos": [
            {"nome": "Bombeiros", "tipo": "bombeiros", "prioridade": 98},
            {"nome": "Caminhao", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Moto", "tipo": "moto", "prioridade": 5},
        ]
    },
}
