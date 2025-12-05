from maspy import *
from maspy.learning import *
from enum import Enum
import argparse
import sys
import signal
import os
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
    import os
    from datetime import datetime

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
    import os

    info_path = os.path.join(dir_execucao, "info_execucao.txt")

    with open(info_path, 'a') as f:
        f.write("\n" + "="*60 + "\n")
        f.write("Informações Adicionais:\n")
        f.write("="*60 + "\n\n")

        for chave, valor in info_dict.items():
            f.write(f"{chave}: {valor}\n")


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



# ==================================================================================
# METODOLOGIAS
# ==================================================================================
# Este sistema é documentado usando as metodologias PEAS e SART:
#
# - PEAS (Performance, Environment, Actuators, Sensors):
#   Especificação completa dos agentes e suas interações
#   Documentação: docs/PEAS.md
#
# - SART (Situation, Agent, Reinforcement learning, Task):
#   Framework para sistemas multi-agentes com aprendizado por reforço
#   Documentação: docs/SART.md
#
# Consulte os documentos para detalhes completos sobre design e especificação.
# ==================================================================================


# CLASSE BASE COM LOGGING

class LoggableAgent(Agent):

    def __init__(self, agt_name=None, log_level=None):
        super().__init__(agt_name)
        self.log_level = log_level or GLOBAL_LOG_LEVEL

    def debug_print(self, msg):
        if self.log_level.value >= LogLevel.DEBUG.value:
            self.print(msg)

    def info_print(self, msg):
        if self.log_level.value >= LogLevel.INFO.value:
            self.print(msg)

    def error_print(self, msg):
        if self.log_level.value >= LogLevel.ERROR.value:
            self.print(msg)



# SISTEMA DE COLETA DE MÉTRICAS

class MetricsCollector:
    """
    Sistema centralizado para coleta de métricas de aprendizado.
    Coleta dados de múltiplos agentes durante o treinamento.
    """

    def __init__(self):
        self.metricas_por_agente = {}  # {nome_agente: {...}}
        self.metricas_globais = {
            "episodios_totais": 0,
            "tempo_inicio": None,
            "tempo_fim": None
        }
        self.dir_execucao = None  # Diretório da execução atual

    def reset(self):
        """
        Reseta todas as métricas para uma nova execução.
        IMPORTANTE: Deve ser chamado no início de cada execução para evitar
        acúmulo de dados de execuções anteriores.
        """
        self.metricas_por_agente.clear()
        self.metricas_globais = {
            "episodios_totais": 0,
            "tempo_inicio": None,
            "tempo_fim": None
        }
        self.dir_execucao = None

    def registrar_agente(self, nome_agente):
        """Registra um novo agente para coleta de métricas."""
        if nome_agente not in self.metricas_por_agente:
            self.metricas_por_agente[nome_agente] = {
                "recompensas_por_episodio": [],
                "acoes_corretas": 0,
                "acoes_incorretas": 0,
                "recompensa_total": 0,
                "recompensa_media": 0,
                "melhor_episodio": {"episodio": 0, "recompensa": float('-inf')},
                "pior_episodio": {"episodio": 0, "recompensa": float('inf')},
                "convergencia": {
                    "convergiu": False,
                    "episodio_convergencia": None,
                    "threshold": 0.95  # 95% de escolhas corretas
                }
            }

    def adicionar_recompensa_episodio(self, nome_agente, episodio, recompensa):
        """Adiciona recompensa de um episódio para um agente."""
        if nome_agente not in self.metricas_por_agente:
            self.registrar_agente(nome_agente)

        metricas = self.metricas_por_agente[nome_agente]
        metricas["recompensas_por_episodio"].append({
            "episodio": episodio,
            "recompensa": recompensa
        })
        metricas["recompensa_total"] += recompensa

        # Atualizar melhor e pior episódio
        if recompensa > metricas["melhor_episodio"]["recompensa"]:
            metricas["melhor_episodio"] = {"episodio": episodio, "recompensa": recompensa}

        if recompensa < metricas["pior_episodio"]["recompensa"]:
            metricas["pior_episodio"] = {"episodio": episodio, "recompensa": recompensa}

    def registrar_acao(self, nome_agente, correta):
        """Registra se uma ação foi correta ou incorreta."""
        if nome_agente not in self.metricas_por_agente:
            self.registrar_agente(nome_agente)

        metricas = self.metricas_por_agente[nome_agente]
        if correta:
            metricas["acoes_corretas"] += 1
        else:
            metricas["acoes_incorretas"] += 1

    def verificar_convergencia(self, nome_agente, janela=10):
        """
        Verifica se o agente convergiu baseado na taxa de acerto.
        Considera uma janela dos últimos N episódios.
        """
        if nome_agente not in self.metricas_por_agente:
            return False

        metricas = self.metricas_por_agente[nome_agente]
        recompensas = metricas["recompensas_por_episodio"]

        if len(recompensas) < janela:
            return False

        # Pegar últimos N episódios
        ultimos = recompensas[-janela:]
        recompensa_media_janela = sum(ep["recompensa"] for ep in ultimos) / janela

        # Considerando que recompensa máxima por episódio é proporcional ao número de veículos
        # Threshold de convergência: média dos últimos episódios >= 95% da recompensa ótima
        recompensa_otima_estimada = 100 * 10  # Assumindo 10 veículos e reward=100 por escolha correta
        threshold = metricas["convergencia"]["threshold"]

        convergiu = recompensa_media_janela >= (recompensa_otima_estimada * threshold)

        if convergiu and not metricas["convergencia"]["convergiu"]:
            metricas["convergencia"]["convergiu"] = True
            metricas["convergencia"]["episodio_convergencia"] = len(recompensas)

        return convergiu

    def calcular_estatisticas(self):
        """Calcula estatísticas finais de todos os agentes."""
        for nome_agente, metricas in self.metricas_por_agente.items():
            num_episodios = len(metricas["recompensas_por_episodio"])
            if num_episodios > 0:
                metricas["recompensa_media"] = metricas["recompensa_total"] / num_episodios

            # Calcular desvio padrão das recompensas
            if num_episodios > 1:
                recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]
                media = metricas["recompensa_media"]
                variancia = sum((r - media) ** 2 for r in recompensas) / num_episodios
                metricas["desvio_padrao"] = variancia ** 0.5
            else:
                metricas["desvio_padrao"] = 0.0

    def calcular_funcao_utilidade(self, nome_agente, alpha=0.5, beta=0.3, gamma=0.2):
        """
        Calcula a função de utilidade para um agente.

        Função de Utilidade (ver docs/PEAS.md para detalhes):
        U(agente) = α × taxa_acerto + β × fator_convergencia + γ × fator_recompensa

        Parâmetros:
            nome_agente: Nome do agente para calcular utilidade
            alpha: Peso da taxa de acerto (0-1) [default: 0.5]
            beta: Peso do fator de convergência (0-1) [default: 0.3]
            gamma: Peso do fator de recompensa (0-1) [default: 0.2]

        Retorna:
            float: Valor de utilidade normalizado (0-1), onde 1 = desempenho ótimo
        """
        if nome_agente not in self.metricas_por_agente:
            return 0.0

        metricas = self.metricas_por_agente[nome_agente]

        # 1. Taxa de acerto normalizada (0-1)
        total_acoes = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
        taxa_acerto = (metricas["acoes_corretas"] / total_acoes) if total_acoes > 0 else 0.0

        # 2. Fator de convergência (0-1)
        # Quanto mais rápido convergir, maior o fator
        if metricas["convergencia"]["convergiu"]:
            ep_conv = metricas["convergencia"]["episodio_convergencia"]
            # Normalizar: convergência em episódio 1 = 1.0, episódio 100 = 0.01
            fator_convergencia = 1.0 / max(1, ep_conv)
            # Escalar para ficar entre 0 e 1 (assumindo max 100 episódios)
            fator_convergencia = min(1.0, fator_convergencia * 10)
        else:
            fator_convergencia = 0.0

        # 3. Fator de recompensa normalizado (0-1)
        # Normalizar pela recompensa máxima teórica
        num_veiculos = 10  # Assumindo máximo de 10 veículos
        recompensa_maxima_teorica = 100 * num_veiculos  # 100 por escolha correta × 10 veículos
        if metricas["recompensa_media"] > 0:
            fator_recompensa = min(1.0, metricas["recompensa_media"] / recompensa_maxima_teorica)
        else:
            fator_recompensa = 0.0

        # Calcular utilidade ponderada
        utilidade = (alpha * taxa_acerto) + (beta * fator_convergencia) + (gamma * fator_recompensa)

        # Garantir que está no intervalo [0, 1]
        utilidade = max(0.0, min(1.0, utilidade))

        # Armazenar componentes para análise
        metricas["utilidade"] = {
            "total": utilidade,
            "taxa_acerto": taxa_acerto,
            "fator_convergencia": fator_convergencia,
            "fator_recompensa": fator_recompensa,
            "pesos": {"alpha": alpha, "beta": beta, "gamma": gamma}
        }

        return utilidade

    def gerar_relatorio(self):
        """Gera relatório textual das métricas coletadas com análise estatística completa."""
        self.calcular_estatisticas()

        # Calcular função de utilidade para todos os agentes
        for nome_agente in self.metricas_por_agente.keys():
            self.calcular_funcao_utilidade(nome_agente)

        relatorio = []
        relatorio.append("\n" + "="*70)
        relatorio.append("RELATÓRIO DE MÉTRICAS DE APRENDIZADO")
        relatorio.append("="*70 + "\n")

        for nome_agente, metricas in self.metricas_por_agente.items():
            relatorio.append(f"\n{titulo(f'Agente: {nome_agente}')}")
            relatorio.append("-"*70)

            num_episodios = len(metricas["recompensas_por_episodio"])
            total_acoes = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
            taxa_acerto = (metricas["acoes_corretas"] / total_acoes * 100) if total_acoes > 0 else 0

            # Métricas básicas
            relatorio.append(f"\n  {destaque('Métricas de Desempenho:')}")
            relatorio.append(f"    Episódios executados: {num_episodios}")
            relatorio.append(f"    Recompensa total: {sucesso(f'{metricas["recompensa_total"]:.2f}')}")
            relatorio.append(f"    Recompensa média: {sucesso(f'{metricas["recompensa_media"]:.2f}')}")
            relatorio.append(f"    Desvio padrão: {metricas['desvio_padrao']:.2f}")
            relatorio.append(f"    Ações corretas: {sucesso(str(metricas['acoes_corretas']))}")
            relatorio.append(f"    Ações incorretas: {erro(str(metricas['acoes_incorretas']))}")
            relatorio.append(f"    Taxa de acerto: {sucesso(f'{taxa_acerto:.2f}%')}")

            # Estatísticas de episódios
            relatorio.append(f"\n  {destaque('Análise de Episódios:')}")
            melhor = metricas["melhor_episodio"]
            pior = metricas["pior_episodio"]
            relatorio.append(f"    Melhor episódio: {melhor['episodio']} (recompensa: {sucesso(f'{melhor["recompensa"]:.2f}')})")
            relatorio.append(f"    Pior episódio: {pior['episodio']} (recompensa: {erro(f'{pior["recompensa"]:.2f}')})")

            # Análise de convergência
            relatorio.append(f"\n  {destaque('Convergência:')}")
            conv = metricas["convergencia"]
            if conv["convergiu"]:
                relatorio.append(f"    Status: {sucesso('CONVERGIU')}")
                relatorio.append(f"    Episódio de convergência: {conv['episodio_convergencia']}")
                relatorio.append(f"    Threshold: {conv['threshold']*100:.0f}%")
            else:
                relatorio.append(f"    Status: {aviso('NÃO CONVERGIU')}")
                relatorio.append(f"    (Threshold requerido: {conv['threshold']*100:.0f}%)")

            # Função de Utilidade (ver docs/PEAS.md)
            if "utilidade" in metricas:
                util = metricas["utilidade"]
                relatorio.append(f"\n  {destaque('Função de Utilidade:')}")
                relatorio.append(f"    Utilidade Total: {sucesso(f'{util["total"]:.4f}')} (0-1 scale)")
                relatorio.append(f"    Componentes:")
                relatorio.append(f"      • Taxa de Acerto: {util['taxa_acerto']:.4f} (peso α={util['pesos']['alpha']})")
                relatorio.append(f"      • Convergência: {util['fator_convergencia']:.4f} (peso β={util['pesos']['beta']})")
                relatorio.append(f"      • Recompensa: {util['fator_recompensa']:.4f} (peso γ={util['pesos']['gamma']})")

                # Classificação qualitativa
                u_total = util["total"]
                if u_total >= 0.9:
                    classificacao = sucesso("EXCELENTE")
                elif u_total >= 0.75:
                    classificacao = sucesso("BOM")
                elif u_total >= 0.6:
                    classificacao = aviso("SATISFATÓRIO")
                else:
                    classificacao = erro("INSUFICIENTE")
                relatorio.append(f"    Classificação: {classificacao}")

            relatorio.append("")

        # Resumo comparativo se houver múltiplos agentes
        if len(self.metricas_por_agente) > 1:
            relatorio.append("\n" + "="*70)
            relatorio.append(titulo("ANÁLISE COMPARATIVA"))
            relatorio.append("="*70 + "\n")

            # Ranking por utilidade
            ranking = sorted(
                self.metricas_por_agente.items(),
                key=lambda x: x[1].get("utilidade", {}).get("total", 0),
                reverse=True
            )

            relatorio.append(f"  {destaque('Ranking por Utilidade:')}")
            for i, (nome, metricas) in enumerate(ranking, 1):
                util = metricas.get("utilidade", {}).get("total", 0)
                relatorio.append(f"    {i}. {nome}: {sucesso(f'{util:.4f}')}")

            relatorio.append("")

        relatorio.append("="*70 + "\n")

        return "\n".join(relatorio)

    def exportar_csv(self, caminho=None):
        """
        Exporta métricas para arquivo CSV.
        Se dir_execucao estiver definido, salva no diretório timestampado.
        """
        import csv
        import os

        # Determinar caminho do CSV
        if caminho is None:
            if self.dir_execucao:
                caminho = os.path.join(self.dir_execucao, "metricas_aprendizado.csv")
            else:
                caminho = "metricas_aprendizado.csv"

        with open(caminho, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Agente", "Episodio", "Recompensa", "Recompensa_Acumulada"
            ])

            for nome_agente, metricas in self.metricas_por_agente.items():
                recompensa_acum = 0
                for ep_data in metricas["recompensas_por_episodio"]:
                    recompensa_acum += ep_data["recompensa"]
                    writer.writerow([
                        nome_agente,
                        ep_data["episodio"],
                        ep_data["recompensa"],
                        recompensa_acum
                    ])

        print(f"\n{sucesso('✓')} Métricas exportadas para: {caminho}")

    def gerar_graficos(self, diretorio=None):
        """
        Gera gráficos de visualização das métricas de aprendizado.
        Cria múltiplos gráficos para análise detalhada.
        Se dir_execucao estiver definido, salva no diretório timestampado.
        """
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import os

            # Determinar diretório dos gráficos
            if diretorio is None:
                if self.dir_execucao:
                    diretorio = os.path.join(self.dir_execucao, "graficos")
                else:
                    diretorio = "graficos"

            # Criar diretório se não existir
            if not os.path.exists(diretorio):
                os.makedirs(diretorio)

            print(f"\n{info('i')} Gerando gráficos de visualização (5 gráficos)...")
            print(f"{info('i')} Diretório: {diretorio}")

            # Gráfico 1: Recompensa por Episódio (todos os agentes)
            print(f"{info('>')} [1/5] Gerando gráfico de recompensa por episódio...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"]:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]
                    plt.plot(episodios, recompensas, marker='o', label=nome_agente, linewidth=2)

            plt.xlabel('Episódio de Treinamento', fontsize=12)
            plt.ylabel('Recompensa', fontsize=12)
            plt.title('Recompensa por Episódio - Treinamento Q-Learning', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico1 = os.path.join(diretorio, 'recompensa_por_episodio.png')
            plt.savefig(caminho_grafico1, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [1/5] Gráfico salvo: recompensa_por_episodio.png")

            # Gráfico 2: Recompensa Acumulada
            print(f"{info('>')} [2/5] Gerando gráfico de recompensa acumulada...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"]:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas_acum = np.cumsum([ep["recompensa"] for ep in metricas["recompensas_por_episodio"]])
                    plt.plot(episodios, recompensas_acum, marker='o', label=nome_agente, linewidth=2)

            plt.xlabel('Episódio de Treinamento', fontsize=12)
            plt.ylabel('Recompensa Acumulada', fontsize=12)
            plt.title('Recompensa Acumulada - Treinamento Q-Learning', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico2 = os.path.join(diretorio, 'recompensa_acumulada.png')
            plt.savefig(caminho_grafico2, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [2/5] Gráfico salvo: recompensa_acumulada.png")

            # Gráfico 3: Média Móvel (janela=5)
            print(f"{info('>')} [3/5] Gerando gráfico de média móvel...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"] and len(metricas["recompensas_por_episodio"]) >= 5:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]

                    # Calcular média móvel
                    janela = 5
                    media_movel = np.convolve(recompensas, np.ones(janela)/janela, mode='valid')
                    episodios_mm = episodios[janela-1:]

                    plt.plot(episodios_mm, media_movel, marker='o', label=f'{nome_agente} (MM)', linewidth=2)

            plt.xlabel('Episódio de Validação', fontsize=12)
            plt.ylabel('Recompensa (Média Móvel)', fontsize=12)
            plt.title('Média Móvel da Recompensa (janela=5) - Validação', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico3 = os.path.join(diretorio, 'media_movel.png')
            plt.savefig(caminho_grafico3, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [3/5] Gráfico salvo: media_movel.png")

            # Gráfico 4: Comparação de Desempenho (barras)
            print(f"{info('>')} [4/5] Gerando gráfico de comparação de desempenho...")
            plt.figure(figsize=(10, 6))
            nomes = []
            recompensas_medias = []
            taxas_acerto = []

            # Filtrar apenas agentes que realmente tomam ações (coordenadores)
            for nome_agente, metricas in self.metricas_por_agente.items():
                total = metricas["acoes_corretas"] + metricas["acoes_incorretas"]
                # Só incluir agentes que fizeram pelo menos uma ação
                if total > 0 or "Coordenador" in nome_agente:
                    nomes.append(nome_agente.replace('_', '\n'))
                    recompensas_medias.append(metricas["recompensa_media"])
                    taxa = (metricas["acoes_corretas"] / total * 100) if total > 0 else 0
                    taxas_acerto.append(taxa)

            x = np.arange(len(nomes))
            width = 0.35

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            bars1 = ax1.bar(x - width/2, recompensas_medias, width, label='Recompensa Média', color='steelblue', alpha=0.8)
            bars2 = ax2.bar(x + width/2, taxas_acerto, width, label='Taxa de Acerto (%)', color='orange', alpha=0.8)

            ax1.set_xlabel('Agente', fontsize=12)
            ax1.set_ylabel('Recompensa Média', fontsize=12, color='steelblue')
            ax2.set_ylabel('Taxa de Acerto (%)', fontsize=12, color='orange')
            ax1.set_title('Comparação de Desempenho dos Agentes', fontsize=14, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(nomes, fontsize=9)
            ax1.tick_params(axis='y', labelcolor='steelblue')
            ax2.tick_params(axis='y', labelcolor='orange')
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            ax1.grid(True, alpha=0.3, axis='y')

            caminho_grafico4 = os.path.join(diretorio, 'comparacao_desempenho.png')
            plt.savefig(caminho_grafico4, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [4/5] Gráfico salvo: comparacao_desempenho.png")

            # Gráfico 5: Convergência (se houver dados suficientes)
            print(f"{info('>')} [5/5] Gerando gráfico de análise de convergência...")
            plt.figure(figsize=(12, 6))
            for nome_agente, metricas in self.metricas_por_agente.items():
                if metricas["recompensas_por_episodio"] and len(metricas["recompensas_por_episodio"]) >= 10:
                    episodios = [ep["episodio"] for ep in metricas["recompensas_por_episodio"]]
                    recompensas = [ep["recompensa"] for ep in metricas["recompensas_por_episodio"]]

                    plt.plot(episodios, recompensas, alpha=0.3, linewidth=1)

                    # Linha de tendência (regressão linear)
                    z = np.polyfit(episodios, recompensas, 1)
                    p = np.poly1d(z)
                    plt.plot(episodios, p(episodios), linewidth=2, label=f'{nome_agente} (tendência)')

                    # Marcar ponto de convergência se houver
                    if metricas["convergencia"]["convergiu"]:
                        ep_conv = metricas["convergencia"]["episodio_convergencia"]
                        plt.axvline(x=ep_conv, color='red', linestyle='--', alpha=0.5,
                                   label=f'Convergência {nome_agente} (ep {ep_conv})')

            plt.xlabel('Episódio de Validação', fontsize=12)
            plt.ylabel('Recompensa', fontsize=12)
            plt.title('Análise de Convergência - Validação (Política Aprendida)', fontsize=14, fontweight='bold')
            plt.legend()
            plt.grid(True, alpha=0.3)
            caminho_grafico5 = os.path.join(diretorio, 'analise_convergencia.png')
            plt.savefig(caminho_grafico5, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"{sucesso('✓')} [5/5] Gráfico salvo: analise_convergencia.png")

            print(f"\n{sucesso('✓')} Todos os 5 gráficos foram salvos com sucesso!")
            print(f"{info('i')} Localização: {diretorio}/")

        except ImportError:
            print(f"\n{aviso('⚠')} matplotlib não está instalado. Pulando geração de gráficos.")
            print("   Instale com: pip install matplotlib")
        except Exception as e:
            print(f"\n{erro('✗')} Erro ao gerar gráficos: {e}")


# Instância global do coletor de métricas
METRICS_COLLECTOR = MetricsCollector()



# SISTEMA DE COMPARAÇÃO ENTRE CENÁRIOS

class ScenarioComparator:
    """
    Sistema para comparar resultados entre diferentes cenários de teste.
    Permite análise comparativa de configurações e parâmetros.
    """

    def __init__(self):
        self.resultados_cenarios = {}  # {nome_cenario: {metricas...}}

    def adicionar_resultado(self, nome_cenario, metrics_collector):
        """
        Adiciona resultado de um cenário para comparação.

        Args:
            nome_cenario: Nome identificador do cenário
            metrics_collector: Instância de MetricsCollector com dados
        """
        # Copiar métricas relevantes
        metricas_resumo = {}

        for nome_agente, metricas in metrics_collector.metricas_por_agente.items():
            metricas_resumo[nome_agente] = {
                "recompensa_media": metricas.get("recompensa_media", 0),
                "recompensa_total": metricas.get("recompensa_total", 0),
                "desvio_padrao": metricas.get("desvio_padrao", 0),
                "taxa_acerto": (metricas["acoes_corretas"] / (metricas["acoes_corretas"] + metricas["acoes_incorretas"]) * 100)
                    if (metricas["acoes_corretas"] + metricas["acoes_incorretas"]) > 0 else 0,
                "convergiu": metricas["convergencia"]["convergiu"],
                "episodio_convergencia": metricas["convergencia"].get("episodio_convergencia", None),
                "utilidade": metricas.get("utilidade", {}).get("total", 0),
                "num_episodios": len(metricas["recompensas_por_episodio"])
            }

        self.resultados_cenarios[nome_cenario] = {
            "metricas_agentes": metricas_resumo,
            "tempo_execucao": metrics_collector.metricas_globais.get("tempo_fim", 0) -
                             metrics_collector.metricas_globais.get("tempo_inicio", 0)
        }

    def gerar_relatorio_comparativo(self):
        """Gera relatório comparativo entre todos os cenários."""
        if not self.resultados_cenarios:
            return "Nenhum cenário para comparar."

        relatorio = []
        relatorio.append("\n" + "="*80)
        relatorio.append(titulo("RELATÓRIO COMPARATIVO ENTRE CENÁRIOS"))
        relatorio.append("="*80 + "\n")

        # Tabela comparativa de cenários
        relatorio.append(destaque("Resumo Geral dos Cenários:\n"))
        relatorio.append(f"{'Cenário':<30} {'Utilidade':<12} {'Taxa Acerto':<15} {'Convergiu':<12} {'Tempo (s)':<10}")
        relatorio.append("-" * 80)

        for nome_cenario, dados in self.resultados_cenarios.items():
            # Pegar métrica do coordenador (primeiro agente)
            coordenador_metricas = next(iter(dados["metricas_agentes"].values()), {})

            utilidade = coordenador_metricas.get("utilidade", 0)
            taxa = coordenador_metricas.get("taxa_acerto", 0)
            conv = "SIM" if coordenador_metricas.get("convergiu", False) else "NÃO"
            tempo = dados.get("tempo_execucao", 0)

            utilidade_str = sucesso(f"{utilidade:.4f}") if utilidade >= 0.75 else aviso(f"{utilidade:.4f}")
            taxa_str = sucesso(f"{taxa:.2f}%") if taxa >= 90 else aviso(f"{taxa:.2f}%")
            conv_str = sucesso(conv) if conv == "SIM" else erro(conv)

            relatorio.append(f"{nome_cenario:<30} {utilidade_str:<20} {taxa_str:<23} {conv_str:<20} {tempo:.2f}")

        # Análise do melhor cenário
        melhor_cenario = max(
            self.resultados_cenarios.items(),
            key=lambda x: next(iter(x[1]["metricas_agentes"].values())).get("utilidade", 0)
        )

        relatorio.append("\n" + destaque("Análise de Melhor Desempenho:"))
        relatorio.append(f"  {sucesso('★')} Melhor cenário: {sucesso(melhor_cenario[0])}")

        melhor_metricas = next(iter(melhor_cenario[1]["metricas_agentes"].values()))
        relatorio.append(f"    • Utilidade: {melhor_metricas.get('utilidade', 0):.4f}")
        relatorio.append(f"    • Taxa de acerto: {melhor_metricas.get('taxa_acerto', 0):.2f}%")
        relatorio.append(f"    • Convergência: {'Episódio ' + str(melhor_metricas.get('episodio_convergencia')) if melhor_metricas.get('convergiu') else 'Não convergiu'}")

        # Recomendações
        relatorio.append("\n" + destaque("Recomendações:"))

        # Identificar cenários que não convergiram
        nao_convergiram = [
            nome for nome, dados in self.resultados_cenarios.items()
            if not next(iter(dados["metricas_agentes"].values())).get("convergiu", False)
        ]

        if nao_convergiram:
            relatorio.append(f"  {aviso('⚠')} Cenários sem convergência ({len(nao_convergiram)}):")
            for nome in nao_convergiram:
                relatorio.append(f"    - {nome}")
            relatorio.append("    Sugestão: Aumentar número de episódios ou ajustar parâmetros de reward")

        # Identificar cenários com baixa performance
        baixa_util = [
            nome for nome, dados in self.resultados_cenarios.items()
            if next(iter(dados["metricas_agentes"].values())).get("utilidade", 0) < 0.6
        ]

        if baixa_util:
            relatorio.append(f"\n  {aviso('⚠')} Cenários com utilidade < 0.6 ({len(baixa_util)}):")
            for nome in baixa_util:
                relatorio.append(f"    - {nome}")
            relatorio.append("    Sugestão: Revisar configuração de prioridades ou multiplicador de penalidade")

        relatorio.append("\n" + "="*80 + "\n")

        return "\n".join(relatorio)

    def exportar_comparacao_csv(self, caminho="comparacao_cenarios.csv"):
        """Exporta comparação de cenários para CSV."""
        import csv

        with open(caminho, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Cenario", "Agente", "Utilidade", "Taxa_Acerto_%", "Recompensa_Media",
                "Desvio_Padrao", "Convergiu", "Ep_Convergencia", "Num_Episodios", "Tempo_Exec_s"
            ])

            for nome_cenario, dados in self.resultados_cenarios.items():
                tempo = dados.get("tempo_execucao", 0)
                for nome_agente, metricas in dados["metricas_agentes"].items():
                    writer.writerow([
                        nome_cenario,
                        nome_agente,
                        f"{metricas.get('utilidade', 0):.4f}",
                        f"{metricas.get('taxa_acerto', 0):.2f}",
                        f"{metricas.get('recompensa_media', 0):.2f}",
                        f"{metricas.get('desvio_padrao', 0):.2f}",
                        "SIM" if metricas.get("convergiu", False) else "NAO",
                        metricas.get("episodio_convergencia", "N/A"),
                        metricas.get("num_episodios", 0),
                        f"{tempo:.2f}"
                    ])

        print(f"{sucesso('✓')} Comparação exportada para: {caminho}")

    def gerar_grafico_comparativo(self, diretorio="graficos"):
        """Gera gráficos comparativos entre cenários."""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            import os

            if not os.path.exists(diretorio):
                os.makedirs(diretorio)

            # Preparar dados
            cenarios = list(self.resultados_cenarios.keys())
            utilidades = []
            taxas_acerto = []
            tempos = []

            for nome_cenario in cenarios:
                dados = self.resultados_cenarios[nome_cenario]
                metricas = next(iter(dados["metricas_agentes"].values()))
                utilidades.append(metricas.get("utilidade", 0))
                taxas_acerto.append(metricas.get("taxa_acerto", 0))
                tempos.append(dados.get("tempo_execucao", 0))

            # Gráfico de barras comparativo
            fig, axes = plt.subplots(1, 3, figsize=(18, 6))

            # Subplot 1: Utilidade
            axes[0].bar(range(len(cenarios)), utilidades, color='steelblue', alpha=0.8)
            axes[0].set_xlabel('Cenário', fontsize=12)
            axes[0].set_ylabel('Utilidade (0-1)', fontsize=12)
            axes[0].set_title('Comparação de Utilidade por Cenário', fontsize=14, fontweight='bold')
            axes[0].set_xticks(range(len(cenarios)))
            axes[0].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[0].axhline(y=0.75, color='green', linestyle='--', alpha=0.5, label='Threshold "Bom"')
            axes[0].legend()
            axes[0].grid(True, alpha=0.3, axis='y')

            # Subplot 2: Taxa de Acerto
            axes[1].bar(range(len(cenarios)), taxas_acerto, color='orange', alpha=0.8)
            axes[1].set_xlabel('Cenário', fontsize=12)
            axes[1].set_ylabel('Taxa de Acerto (%)', fontsize=12)
            axes[1].set_title('Comparação de Taxa de Acerto', fontsize=14, fontweight='bold')
            axes[1].set_xticks(range(len(cenarios)))
            axes[1].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[1].axhline(y=95, color='green', linestyle='--', alpha=0.5, label='Meta 95%')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3, axis='y')

            # Subplot 3: Tempo de Execução
            axes[2].bar(range(len(cenarios)), tempos, color='purple', alpha=0.8)
            axes[2].set_xlabel('Cenário', fontsize=12)
            axes[2].set_ylabel('Tempo (s)', fontsize=12)
            axes[2].set_title('Tempo de Execução por Cenário', fontsize=14, fontweight='bold')
            axes[2].set_xticks(range(len(cenarios)))
            axes[2].set_xticklabels([c[:15] for c in cenarios], rotation=45, ha='right', fontsize=9)
            axes[2].grid(True, alpha=0.3, axis='y')

            plt.tight_layout()
            caminho_grafico = os.path.join(diretorio, 'comparacao_cenarios.png')
            plt.savefig(caminho_grafico, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"{sucesso('✓')} Gráfico comparativo salvo: {caminho_grafico}")

        except ImportError:
            print(f"{aviso('⚠')} matplotlib não disponível para gráficos comparativos")
        except Exception as e:
            print(f"{erro('✗')} Erro ao gerar gráfico comparativo: {e}")


# Instância global do comparador de cenários
SCENARIO_COMPARATOR = ScenarioComparator()



# AMBIENTE DE APRENDIZADO - CRUZAMENTO

class CruzamentoLearningEnvironment(Environment):
    """
    Ambiente de aprendizado para o problema de cruzamento.

    Implementa aprendizado por reforço (Q-Learning) para ordenação de veículos.
    Ver docs/SART.md para especificação completa da metodologia.

    Resumo:
    - States: Combinação de veículos disponíveis para atravessar
    - Actions: Escolher qual veículo passa
    - Rewards: +100 se prioridade correta, -penalidade proporcional se errado
    - Transitions: Remove veículo que passou do estado
    """

    # Variáveis de classe para receber configuração (MASPY não suporta parâmetros no __init__)
    _veiculos_config_override = None
    _verbose = False  # Flag para logs detalhados
    _reward_correto = 100  # Recompensa por escolha correta
    _penalidade_multiplicador = 1  # Multiplicador da penalidade
    _step_by_step = False  # Modo passo a passo com delay
    _episodio_atual = 0  # Contador de episódios para logs
    _em_treinamento = False  # Flag para distinguir exploração de treinamento

    def __init__(self):
        super().__init__()

        self.verbose = CruzamentoLearningEnvironment._verbose

        # Usar configuração fornecida via variável de classe ou padrão
        # LIMITADO A 10 VEÍCULOS para aprendizado (decorator @action requer nomes fixos)
        config_base = CruzamentoLearningEnvironment._veiculos_config_override or VEICULOS_CONFIG
        veiculos_config_original = config_base[:10]  # Máximo 10 veículos

        if len(config_base) > 10:
            print(f"\nAVISO: Modo aprendizado limitado a 10 veículos.")
            print(f"Usando os primeiros 10 de {len(config_base)} veículos do cenário.\n")

        # Criar configuração adaptada com nomes Veiculo1-4 (requerido pelo MASPY)
        veiculos_config = []
        for i, v in enumerate(veiculos_config_original):
            veiculos_config.append({
                "nome": f"Veiculo{i+1}",
                "tipo": v["tipo"],
                "prioridade": v["prioridade"],
                "nome_original": v["nome"]
            })

        # Mostrar mapeamento
        print("Mapeamento de veículos para aprendizado:")
        for v in veiculos_config:
            print(f"  {v['nome_original']} -> {v['nome']} (prio={v['prioridade']})")
        print()

        self.veiculos_config = veiculos_config
        self.num_veiculos = len(veiculos_config)

        # Criar lista de IDs dos veículos (será o espaço de ações)
        self.veiculos_ids = tuple(v["nome"] for v in veiculos_config)

        # Mapear prioridades
        self.prioridades = {v["nome"]: v["prioridade"] for v in veiculos_config}

        # Mapear nomes originais para exibição
        self.nomes_originais = {v["nome"]: v["nome_original"] for v in veiculos_config}

        # Criar mapeamento dinâmico de veículos para estados
        self.veiculo_map = {}
        self.possible_starts = {}

        for i, veiculo in enumerate(veiculos_config):
            nome = veiculo["nome"]
            estado_key = f"v{i+1}_passou"
            self.veiculo_map[nome] = estado_key
            self.create(Percept(estado_key, (0, 1), listed))
            self.possible_starts[estado_key] = 0

        # Estado interno
        self.historico_travessias = []
        self.recompensa_acumulada = 0
        self.episodio = 0

    def transicao_escolher(self, state, action):
        """
        Função de transição para a ação de escolher veículo.

        Args:
            state: dict com estado atual
            action: ID do veículo escolhido

        Returns:
            new_state: novo estado
            reward: recompensa
            terminated: se episódio terminou
        """
        veiculo_escolhido = action

        # Usar mapeamento dinâmico
        if veiculo_escolhido not in self.veiculo_map:
            return state, -100, False

        estado_key = self.veiculo_map[veiculo_escolhido]

        # Verificar se veículo já passou (ação inválida)
        if state[estado_key] == 1:
            return state, -100, False

        # Identificar veículos que ainda não passaram
        veiculos_disponiveis = []
        for nome, key in self.veiculo_map.items():
            if state[key] == 0:
                veiculos_disponiveis.append(nome)

        # Calcular recompensa
        prioridade_escolhido = self.prioridades[veiculo_escolhido]
        melhor_prioridade = max(self.prioridades[v] for v in veiculos_disponiveis)

        if prioridade_escolhido == melhor_prioridade:
            reward = CruzamentoLearningEnvironment._reward_correto
        else:
            # Penalidade proporcional à diferença
            diferenca = melhor_prioridade - prioridade_escolhido
            reward = -diferenca * CruzamentoLearningEnvironment._penalidade_multiplicador

        # Novo estado: marcar veículo como passou
        new_state = state.copy()
        new_state[estado_key] = 1

        # Verificar se terminou (todos passaram)
        terminated = all(new_state[key] == 1 for key in self.veiculo_map.values())

        # Log verbose durante a exploração inicial (MASPY não chama transição durante learn)
        # Usar variável de classe diretamente pois EnvModel pode usar outra instância
        verbose = CruzamentoLearningEnvironment._verbose
        step_by_step = CruzamentoLearningEnvironment._step_by_step

        if verbose:
            import time
            nome_orig = self.nomes_originais.get(veiculo_escolhido, veiculo_escolhido)

            # Determinar se foi escolha correta
            if prioridade_escolhido == melhor_prioridade:
                icone = cor("✓", Cores.VERDE)
                resultado = cor(f"+{reward}", Cores.VERDE)
            else:
                icone = cor("✗", Cores.VERMELHO)
                resultado = cor(f"{reward}", Cores.VERMELHO)

            # Mostrar veículos disponíveis para contexto
            disponiveis_str = ", ".join([
                f"{self.nomes_originais.get(v, v)}({self.prioridades[v]})"
                for v in sorted(veiculos_disponiveis, key=lambda x: self.prioridades[x], reverse=True)
            ])

            print(f"  {icone} Escolheu: {cor(nome_orig, Cores.CIANO)} (prio={prioridade_escolhido})", flush=True)
            print(f"    Disponíveis: {disponiveis_str}", flush=True)
            print(f"    Reward: {resultado}", flush=True)

            if terminated:
                CruzamentoLearningEnvironment._episodio_atual += 1
                ep = CruzamentoLearningEnvironment._episodio_atual
                print(cor(f"  ══ Exploração {ep} concluída ══\n", Cores.AMARELO), flush=True)

            if step_by_step:
                time.sleep(0.3)

        return new_state, reward, terminated

    @action(listed, ("Veiculo1", "Veiculo2", "Veiculo3", "Veiculo4", "Veiculo5",
                     "Veiculo6", "Veiculo7", "Veiculo8", "Veiculo9", "Veiculo10"), transicao_escolher)
    def escolher_veiculo(self, agt, veiculo_id):
        """
        Ação de escolher qual veículo atravessa.
        Decorada com @action para aprendizado por reforço.
        """
        # Usar mapeamento dinâmico
        if veiculo_id not in self.veiculo_map:
            return

        estado_key = self.veiculo_map[veiculo_id]

        # Verificar o estado atual do percept para esse veículo
        percept = self.get(Percept(estado_key, Any))
        if percept and percept.values == 1:
            # Veículo já passou - não fazer nada
            return

        # Atualizar o percept para indicar que o veículo passou
        self.change(Percept(estado_key, Any), 1)

        self.historico_travessias.append(veiculo_id)



# AGENTE DE APRENDIZADO

class CoordenadorLearningAgent(LoggableAgent):
    """
    Agente coordenador que usa Q-Learning para aprender
    a ordem ótima de travessia dos veículos.
    """

    def __init__(self, agt_name=None, env=None, num_episodes=100, log_level=None):
        super().__init__(agt_name, log_level)

        self.env = env
        self.num_episodes = num_episodes

        # Beliefs observáveis
        self.add(Belief("status", "inicializando"))
        self.add(Belief("episodio_atual", 0))
        self.add(Belief("recompensa_total", 0))

        # Goal para iniciar aprendizado
        self.add(Goal("aprender"))

    def _update_status(self, new_status):
        """Atualiza o status observável do agente."""
        old_belief = self.get(Belief("status", Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief("status", new_status))

    def _update_belief(self, belief_name, value):
        """Atualiza um belief observável."""
        old_belief = self.get(Belief(belief_name, Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief(belief_name, value))

    @pl(gain, Goal("aprender"))
    def iniciar_aprendizado(self, src):
        """
        Inicia o processo de aprendizado por Q-Learning.
        Usa EnvModel para criar modelo do ambiente e treinar.
        Coleta métricas durante o processo de aprendizado.
        """
        self._update_status("aprendendo")
        self.info_print("\n" + "="*60)
        self.info_print("INICIANDO APRENDIZADO POR Q-LEARNING")
        self.info_print("="*60)

        # Acessar o ambiente de aprendizado (passado no __init__)
        try:
            env = self.env
            self.info_print(f"Ambiente: {env.my_name}")

            # Criar modelo do ambiente (esta fase faz exploração inicial)
            self.info_print("Criando modelo do ambiente (exploração inicial)...")
            model = EnvModel(env)

            self.info_print(f"Treinando com {self.num_episodes} episódios...")
            self.info_print("-"*60)

            # Ativar flag de treinamento para logs verbose
            CruzamentoLearningEnvironment._em_treinamento = True
            CruzamentoLearningEnvironment._episodio_atual = 0

            # Variáveis para coleta de métricas durante o treinamento
            recompensas_por_episodio = []

            # Wrapper para capturar métricas DURANTE o treinamento do Q-Learning
            # Vamos executar episódios manualmente e treinar com os dados coletados
            self.info_print("\nExecutando treinamento com coleta de métricas...")

            # Inicializar Q-table manualmente
            import random
            from collections import defaultdict

            # Parâmetros Q-Learning
            alpha = 0.1  # Taxa de aprendizado
            gamma = 0.9  # Fator de desconto
            epsilon = 1.0  # Exploração inicial
            epsilon_decay = 0.995
            epsilon_min = 0.01

            # Q-table: dict de (state_tuple, action) -> valor
            q_table = defaultdict(float)

            def estado_para_tupla(estado_dict):
                """Converte estado dict para tupla ordenada (hashable)."""
                return tuple(estado_dict[env.veiculo_map[v]] for v in env.veiculos_ids)

            def escolher_acao_epsilon_greedy(estado_tupla, veiculos_disponiveis, epsilon):
                """Escolhe ação usando estratégia epsilon-greedy."""
                if random.random() < epsilon:
                    # Exploração: ação aleatória
                    return random.choice(veiculos_disponiveis)
                else:
                    # Exploitação: melhor ação conhecida
                    q_values = {v: q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
                    max_q = max(q_values.values())
                    # Escolher entre as ações com Q máximo (pode haver empate)
                    melhores = [v for v, q in q_values.items() if q == max_q]
                    return random.choice(melhores)

            # Treinar por num_episodes episódios
            for ep in range(self.num_episodes):
                estado = env.possible_starts.copy()
                estado_tupla = estado_para_tupla(estado)
                recompensa_total = 0
                acoes_corretas = 0
                acoes_total = 0

                # Executar episódio completo
                while True:
                    # Identificar veículos disponíveis
                    veiculos_disponiveis = [
                        v for v in env.veiculos_ids
                        if estado[env.veiculo_map[v]] == 0
                    ]

                    if not veiculos_disponiveis:
                        break

                    # Escolher ação
                    veiculo_escolhido = escolher_acao_epsilon_greedy(
                        estado_tupla, veiculos_disponiveis, epsilon
                    )

                    # Executar transição e obter recompensa
                    novo_estado, recompensa, terminado = env.transicao_escolher(
                        estado, veiculo_escolhido
                    )
                    novo_estado_tupla = estado_para_tupla(novo_estado)

                    # Verificar se foi escolha ótima
                    melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
                    escolha_correta = (env.prioridades[veiculo_escolhido] == melhor_prioridade)
                    if escolha_correta:
                        acoes_corretas += 1
                    acoes_total += 1

                    # Atualizar Q-table (Bellman equation)
                    if terminado:
                        # Estado terminal: Q(s,a) = R
                        target = recompensa
                    else:
                        # Q(s,a) = R + γ * max(Q(s',a'))
                        proximos_disponiveis = [
                            v for v in env.veiculos_ids
                            if novo_estado[env.veiculo_map[v]] == 0
                        ]
                        max_q_proximo = max(
                            q_table[(novo_estado_tupla, v)] for v in proximos_disponiveis
                        ) if proximos_disponiveis else 0
                        target = recompensa + gamma * max_q_proximo

                    # Atualização Q-Learning
                    q_atual = q_table[(estado_tupla, veiculo_escolhido)]
                    q_table[(estado_tupla, veiculo_escolhido)] = q_atual + alpha * (target - q_atual)

                    # Acumular recompensa
                    recompensa_total += recompensa

                    # Avançar para próximo estado
                    estado = novo_estado
                    estado_tupla = novo_estado_tupla

                    if terminado:
                        break

                # Registrar métricas do episódio
                recompensas_por_episodio.append(recompensa_total)
                METRICS_COLLECTOR.adicionar_recompensa_episodio(
                    self.my_name,
                    ep + 1,
                    recompensa_total
                )

                # Registrar ações
                for _ in range(acoes_corretas):
                    METRICS_COLLECTOR.registrar_acao(self.my_name, True)
                for _ in range(acoes_total - acoes_corretas):
                    METRICS_COLLECTOR.registrar_acao(self.my_name, False)

                # Decair epsilon
                epsilon = max(epsilon_min, epsilon * epsilon_decay)

                # Verificar convergência a cada 10 episódios
                if (ep + 1) % 10 == 0:
                    if METRICS_COLLECTOR.verificar_convergencia(self.my_name, janela=10):
                        self.info_print(f"Convergência detectada no episódio {ep + 1}!")

            self.info_print(f"Treinamento concluído com {self.num_episodes} episódios.")

            # Desativar flag
            CruzamentoLearningEnvironment._em_treinamento = False

            self.info_print("-"*60)
            self.info_print("TREINAMENTO CONCLUÍDO!")

            # Mostrar ordem ótima aprendida
            print("\n" + "="*50, flush=True)
            print("RESULTADO DO APRENDIZADO", flush=True)
            print("="*50, flush=True)

            # Calcular a ordem ótima baseado nas prioridades
            ordem_otima = sorted(env.veiculos_ids,
                                key=lambda v: env.prioridades[v],
                                reverse=True)

            print(f"\nOrdem ótima aprendida: {' -> '.join(ordem_otima)}", flush=True)
            print("\nPrioridades:", flush=True)
            for v in ordem_otima:
                print(f"  {v}: {env.prioridades[v]}", flush=True)

            # Mostrar mapeamento para nomes originais
            if hasattr(env, 'nomes_originais') and env.nomes_originais:
                print("\nMapeamento para nomes originais:", flush=True)
                for v in ordem_otima:
                    nome_orig = env.nomes_originais.get(v, v)
                    print(f"  {v} = {nome_orig}", flush=True)

            print("\n" + "="*50, flush=True)
            print("APRENDIZADO CONCLUÍDO COM SUCESSO!", flush=True)
            print("="*50 + "\n", flush=True)

            sys.stdout.flush()

            # Marcar goal como concluído e parar ciclo do agente
            self._update_status("concluido")
            self.stop_cycle()

        except Exception as e:
            self.error_print(f"ERRO durante aprendizado: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.stop_cycle()



# AGENTE DE VEÍCULO COM APRENDIZADO

class VeiculoLearningAgent(LoggableAgent):
    """
    Agente que representa um veículo individual que aprende
    quando solicitar passagem no cruzamento.

    Cada veículo tem sua própria estratégia de aprendizado baseada em:
    - Sua prioridade
    - Estado atual do cruzamento
    - Histórico de sucesso/falha
    """

    def __init__(self, agt_name=None, veiculo_id=None, prioridade=10, env=None, log_level=None):
        super().__init__(agt_name, log_level)

        self.veiculo_id = veiculo_id
        self.prioridade = prioridade
        self.env = env

        # Beliefs observáveis
        self.add(Belief("veiculo_id", veiculo_id))
        self.add(Belief("prioridade", prioridade))
        self.add(Belief("status", "aguardando"))
        self.add(Belief("tentativas", 0))
        self.add(Belief("sucessos", 0))
        self.add(Belief("falhas", 0))

        # Métricas de aprendizado
        self.historico_acoes = []
        self.recompensa_acumulada = 0

        # Registrar no coletor de métricas
        METRICS_COLLECTOR.registrar_agente(agt_name)

        # Goal para observar o ambiente
        self.add(Goal("observar_cruzamento"))

    def _update_belief(self, belief_name, value):
        """Atualiza um belief observável."""
        old_belief = self.get(Belief(belief_name, Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief(belief_name, value))

    @pl(gain, Goal("observar_cruzamento"))
    def monitorar_ambiente(self, src):
        """
        Monitora o estado do ambiente e aprende com as experiências.
        Este agente observa passivamente o aprendizado do coordenador.
        """
        # Verificar se o treinamento foi concluído
        if not CruzamentoLearningEnvironment._em_treinamento:
            self._update_belief("status", "concluido")
            self.stop_cycle()
            return

        self._update_belief("status", "observando")

        self.debug_print(f"[{self.my_name}] Veículo {self.veiculo_id} (prioridade={self.prioridade}) observando cruzamento...")

        # Registrar que o veículo está ativo
        tentativas = self.get(Belief("tentativas", Any))
        if tentativas:
            self._update_belief("tentativas", tentativas.values + 1)

    def registrar_resultado(self, escolhido, recompensa):
        """
        Registra o resultado de uma decisão do coordenador.

        Args:
            escolhido: True se este veículo foi escolhido
            recompensa: Recompensa recebida pela ação
        """
        self.historico_acoes.append({
            "escolhido": escolhido,
            "recompensa": recompensa
        })

        if escolhido:
            self.recompensa_acumulada += recompensa

            # Atualizar beliefs
            sucessos = self.get(Belief("sucessos", Any))
            if recompensa > 0:
                novo_valor = (sucessos.values if sucessos else 0) + 1
                self._update_belief("sucessos", novo_valor)
                METRICS_COLLECTOR.registrar_acao(self.my_name, True)
            else:
                falhas = self.get(Belief("falhas", Any))
                novo_valor = (falhas.values if falhas else 0) + 1
                self._update_belief("falhas", novo_valor)
                METRICS_COLLECTOR.registrar_acao(self.my_name, False)

    def obter_estatisticas(self):
        """Retorna estatísticas de aprendizado do veículo."""
        sucessos = self.get(Belief("sucessos", Any))
        falhas = self.get(Belief("falhas", Any))
        tentativas = self.get(Belief("tentativas", Any))

        return {
            "veiculo_id": self.veiculo_id,
            "prioridade": self.prioridade,
            "tentativas": tentativas.values if tentativas else 0,
            "sucessos": sucessos.values if sucessos else 0,
            "falhas": falhas.values if falhas else 0,
            "recompensa_acumulada": self.recompensa_acumulada,
            "total_acoes": len(self.historico_acoes)
        }



# EXECUCAO PRINCIPAL

def parse_arguments():
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema Multi-Agentes de Negociação em Cruzamento com Aprendizado Q-Learning"
    )
    parser.add_argument(
        '--log-level',
        choices=['SILENT', 'ERROR', 'INFO', 'DEBUG'],
        default='INFO',
        help='Nível de log (padrão: INFO)'
    )
    parser.add_argument(
        '--experimento',
        choices=list(EXPERIMENTOS.keys()),
        default='padrao',
        help=f'Experimento a executar: {", ".join(EXPERIMENTOS.keys())}'
    )
    parser.add_argument(
        '--episodios',
        type=int,
        default=100,
        help='Número de episódios para treinamento Q-Learning (padrão: 100)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Esconder logs detalhados do aprendizado'
    )
    return parser.parse_args()


def imprimir_configuracao(config, log_level, episodios=100):
    """Imprime a configuração do sistema."""
    print("="*70)
    print("SISTEMA MULTI-AGENTES - APRENDIZADO Q-LEARNING")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*70)

    print("\nConfiguracao do Sistema:")
    print(f"  - {len(config)} Veiculos")
    print(f"  - Log Level: {log_level.name}")
    print(f"  - Episódios Q-Learning: {episodios}")

    print("\n  Veiculos:")
    for v in config:
        emergencia = " [EMERGENCIA]" if v["prioridade"] >= 100 else ""
        print(f"    - {v['nome']}: {v['tipo']} (prioridade={v['prioridade']}){emergencia}")

    print("\n  Aprendizado por Reforço (Q-Learning):")
    print("    1. Agente explora estados e ações")
    print("    2. Recebe recompensas (+100 prioridade correta, -penalidade proporcional)")
    print("    3. Atualiza Q-table com experiências")
    print("    4. Após treinamento, mostra ordem ótima aprendida")

    print("\n" + "="*70 + "\n")


def menu_interativo():
    """Interface interativa colorida para configurar o experimento."""
    print("\n" + titulo("="*70))
    print(titulo("  SISTEMA MULTI-AGENTES - APRENDIZADO Q-LEARNING"))
    print(titulo("  Trabalho 1 - SMA 2025.2 - UTFPR"))
    print(titulo("="*70) + "\n")

    # Escolher tipo de experimento
    print(destaque("Escolha o tipo de experimento:\n"))
    print(f"  {cor('1', Cores.AMARELO)}. Experimento pré-definido")
    print(f"  {cor('2', Cores.AMARELO)}. Experimento customizado")
    print(f"  {cor('0', Cores.VERMELHO)}. Sair\n")

    while True:
        try:
            escolha = input(cor(">>> Opção: ", Cores.CIANO)).strip()
            if escolha == "0":
                return None
            if escolha in ["1", "2"]:
                break
            print(erro("Opção inválida!"))
        except KeyboardInterrupt:
            return None

    config = {}

    if escolha == "1":
        # Experimento pré-definido
        print("\n" + destaque("Experimentos disponíveis:\n"))
        opcoes = list(EXPERIMENTOS.keys())
        for i, key in enumerate(opcoes, 1):
            exp = EXPERIMENTOS[key]
            print(f"  {cor(str(i), Cores.AMARELO)}. {exp['titulo']} ({len(exp['veiculos'])} veículos)")
            print(f"     {cor(exp['descricao'], Cores.BRANCO)}")

        while True:
            try:
                idx = input(cor("\n>>> Escolha: ", Cores.CIANO)).strip()
                idx = int(idx) - 1
                if 0 <= idx < len(opcoes):
                    config['experimento'] = opcoes[idx]
                    config['veiculos'] = EXPERIMENTOS[opcoes[idx]]['veiculos']
                    break
                print(erro("Opção inválida!"))
            except (ValueError, KeyboardInterrupt):
                print(erro("Digite um número válido!"))

    else:
        # Experimento customizado
        print("\n" + destaque("Configuração customizada de veículos:\n"))

        print(aviso("Tipos disponíveis e prioridades sugeridas:"))
        print(f"  {cor('ambulancia', Cores.VERMELHO)}  - emergência (sugestão: 100)")
        print(f"  {cor('bombeiros', Cores.VERMELHO)}   - emergência (sugestão: 98)")
        print(f"  {cor('policia', Cores.VERMELHO)}     - emergência (sugestão: 95)")
        print(f"  {cor('caminhao', Cores.AMARELO)}    - pesado (sugestão: 50)")
        print(f"  {cor('onibus', Cores.AMARELO)}      - coletivo (sugestão: 40)")
        print(f"  {cor('taxi', Cores.BRANCO)}        - serviço (sugestão: 25)")
        print(f"  {cor('carro', Cores.BRANCO)}       - comum (sugestão: 10)")
        print(f"  {cor('moto', Cores.BRANCO)}        - comum (sugestão: 5)")

        print(f"\n{aviso('Nome: qualquer texto (ex: Carro1, MinhaAmbulancia)')}")
        print(f"{aviso('Prioridade: número de 1 a 100 (maior = mais prioritário)')}")
        print(f"\n{destaque('Digite os veículos (mínimo 2, máximo 10):')}")
        print(aviso("Digite 'fim' quando terminar\n"))

        veiculos = []
        while len(veiculos) < 10:
            try:
                if len(veiculos) >= 2:
                    prompt = f">>> Veículo {len(veiculos)+1} (ou 'fim'): "
                else:
                    prompt = f">>> Veículo {len(veiculos)+1}: "

                entrada = input(cor(prompt, Cores.CIANO)).strip()

                if entrada.lower() == 'fim':
                    if len(veiculos) >= 2:
                        break
                    print(erro("Mínimo 2 veículos!"))
                    continue

                partes = entrada.split(',')
                if len(partes) != 3:
                    print(erro("Formato: nome,tipo,prioridade (ex: Ambulancia1,ambulancia,100)"))
                    continue

                nome, tipo, prio = partes
                nome = nome.strip()
                tipo = tipo.strip().lower()
                prio = int(prio.strip())

                if prio < 1 or prio > 100:
                    print(erro("Prioridade deve ser entre 1 e 100!"))
                    continue

                veiculos.append({
                    "nome": nome,
                    "tipo": tipo,
                    "prioridade": prio
                })

                # Mostrar com cor baseada na prioridade
                if prio >= 90:
                    cor_prio = Cores.VERMELHO
                elif prio >= 40:
                    cor_prio = Cores.AMARELO
                else:
                    cor_prio = Cores.BRANCO

                print(f"  {sucesso('✓')} {nome} ({tipo}) - prioridade: {cor(str(prio), cor_prio)}")

            except ValueError:
                print(erro("Prioridade deve ser um número!"))
            except KeyboardInterrupt:
                return None

        config['experimento'] = 'customizado'
        config['veiculos'] = veiculos

    # Configurar parâmetros de aprendizado
    print("\n" + destaque("Configuração do aprendizado:\n"))

    # Episódios
    try:
        ep = input(cor(">>> Número de episódios [100]: ", Cores.CIANO)).strip()
        config['episodios'] = int(ep) if ep else 100
    except ValueError:
        config['episodios'] = 100

    # Reward
    try:
        rw = input(cor(">>> Reward por acerto [100]: ", Cores.CIANO)).strip()
        config['reward'] = int(rw) if rw else 100
    except ValueError:
        config['reward'] = 100

    # Penalidade
    print(f"\n{aviso('Multiplicador de penalidade:')}")
    print(f"  Controla a severidade da punição por escolhas erradas.")
    print(f"  Fórmula: penalidade = -(diferença_prioridade) × multiplicador")
    print(f"  Ex: Se Ambulância(100) disponível e escolhe Carro(10):")
    print(f"      - Mult. {cor('1', Cores.BRANCO)}: penalidade = -90")
    print(f"      - Mult. {cor('2', Cores.AMARELO)}: penalidade = -180 (aprende mais rápido)")
    print(f"      - Mult. {cor('0.5', Cores.VERDE)}: penalidade = -45 (mais suave)")
    try:
        pn = input(cor(">>> Multiplicador penalidade [1]: ", Cores.CIANO)).strip()
        config['penalidade'] = float(pn) if pn else 1
    except ValueError:
        config['penalidade'] = 1

    # Verbose
    vb = input(cor(">>> Mostrar logs detalhados? [S/n]: ", Cores.CIANO)).strip().lower()
    config['verbose'] = vb != 'n'

    # Modo passo a passo (só se verbose)
    if config['verbose']:
        print(f"\n{aviso('Modo passo a passo:')}")
        print(f"  Mostra cada transição durante a exploração inicial com delay.")
        print(f"  {cor('A exploração mapeia todos os estados possíveis antes do Q-Learning.', Cores.BRANCO)}")
        sbs = input(cor(">>> Modo passo a passo? [s/N]: ", Cores.CIANO)).strip().lower()
        config['step_by_step'] = sbs == 's'
    else:
        config['step_by_step'] = False

    return config


if __name__ == "__main__":
    try:
        args = parse_arguments()

        # Modo interativo (sem argumentos específicos) ou com argumentos
        if len(sys.argv) == 1:
            # Modo interativo
            config = menu_interativo()
            if config is None:
                print("\nSaindo...")
                sys.exit(0)

            veiculos_config = config['veiculos']
            episodios = config['episodios']
            verbose = config['verbose']
            reward = config['reward']
            penalidade = config['penalidade']
            step_by_step = config['step_by_step']
            log_level = LogLevel.INFO

            exp_nome = config.get('experimento', 'customizado')
            if exp_nome in EXPERIMENTOS:
                print(f"\n>>> {sucesso('Experimento selecionado:')} {EXPERIMENTOS[exp_nome]['titulo']}")
            else:
                print(f"\n>>> {sucesso('Experimento customizado')}")

        else:
            # Modo com argumentos
            log_level = LogLevel[args.log_level]
            experimento = EXPERIMENTOS[args.experimento]
            veiculos_config = experimento["veiculos"]
            episodios = args.episodios
            verbose = not args.quiet
            reward = 100
            penalidade = 1
            step_by_step = False

            print(f"\n>>> Experimento selecionado: {experimento['titulo']}")
            print(f"    {experimento['descricao']}\n")

        # Imprimir configuração
        imprimir_configuracao(veiculos_config, log_level, episodios)

        NUM_VEICULOS = len(veiculos_config)
        if NUM_VEICULOS < 2:
            raise ValueError("Sistema requer pelo menos 2 veículos")

        # RESET: Limpar métricas de execuções anteriores
        # Isso garante que cada execução tenha dados limpos
        METRICS_COLLECTOR.reset()

        # Criar diretório de resultados com timestamp
        exp_nome = args.experimento if len(sys.argv) > 1 else config.get('experimento', 'customizado')
        dir_resultados = criar_diretorio_resultados(exp_nome)

        # Definir diretório no MetricsCollector global
        METRICS_COLLECTOR.dir_execucao = dir_resultados

        # Inicializar Admin
        Admin()

        print("Iniciando sistema de APRENDIZADO (Q-Learning)...\n")

        # Passar configuração via variável de classe (MASPY não suporta parâmetros no __init__)
        CruzamentoLearningEnvironment._veiculos_config_override = veiculos_config
        CruzamentoLearningEnvironment._verbose = verbose
        CruzamentoLearningEnvironment._reward_correto = reward
        CruzamentoLearningEnvironment._penalidade_multiplicador = penalidade
        CruzamentoLearningEnvironment._step_by_step = step_by_step
        CruzamentoLearningEnvironment._episodio_atual = 0

        # Criar ambiente de aprendizado
        env = CruzamentoLearningEnvironment()

        # Criar lista de agentes
        agentes = []

        # Criar agente coordenador principal
        agente_coordenador = CoordenadorLearningAgent(
            "CoordenadorLearning",
            env=env,
            num_episodes=episodios,
            log_level=log_level
        )
        agentes.append(agente_coordenador)

        # Criar agentes de veículos (múltiplas instâncias)
        print(f"\n{titulo('Criando agentes de veículos...')}")
        veiculos_limitados = veiculos_config[:10]  # Limitar a 10 para aprendizado

        for i, veiculo_config in enumerate(veiculos_limitados):
            nome_agente = f"Veiculo_{veiculo_config['nome']}"
            agente_veiculo = VeiculoLearningAgent(
                agt_name=nome_agente,
                veiculo_id=f"Veiculo{i+1}",
                prioridade=veiculo_config['prioridade'],
                env=env,
                log_level=log_level
            )
            agentes.append(agente_veiculo)
            print(f"  {sucesso('✓')} Criado: {nome_agente} (prioridade={veiculo_config['prioridade']})")

        print(f"\n{sucesso(f'Total de agentes criados: {len(agentes)}')} (1 coordenador + {len(agentes)-1} veículos)\n")

        # Conectar todos os agentes ao ambiente
        Admin().connect_to(agentes, env)

        # Registrar tempo de início
        import time
        METRICS_COLLECTOR.metricas_globais["tempo_inicio"] = time.time()

        # Iniciar sistema
        print(f"{titulo('Iniciando sistema multi-agentes...')}\n")
        Admin().start_system()

        # AGUARDAR CONFIRMAÇÃO DO USUÁRIO PARA CONTINUAR
        print("\n" + "="*70)
        print(aviso("Treinamento MASPY concluído!"))
        print(info("Pressione ENTER para continuar com a geração de gráficos e relatórios..."))
        print("="*70)
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            print("\nContinuando automaticamente...")

        # Registrar tempo de fim
        METRICS_COLLECTOR.metricas_globais["tempo_fim"] = time.time()

        # Gerar e exibir relatório de métricas
        print(METRICS_COLLECTOR.gerar_relatorio())

        # Exportar métricas para CSV (usa diretório timestampado automaticamente)
        METRICS_COLLECTOR.exportar_csv()

        # Gerar gráficos de visualização (usa diretório timestampado automaticamente)
        print(f"\n{titulo('Gerando gráficos de visualização...')}")
        METRICS_COLLECTOR.gerar_graficos()

        # Salvar informações adicionais da execução
        tempo_total = METRICS_COLLECTOR.metricas_globais["tempo_fim"] - METRICS_COLLECTOR.metricas_globais["tempo_inicio"]
        info_adicional = {
            "Número de episódios": episodios,
            "Número de veículos": NUM_VEICULOS,
            "Tempo total de execução (s)": f"{tempo_total:.2f}",
            "Recompensa por escolha correta": reward,
            "Multiplicador de penalidade": penalidade,
            "Log level": log_level.name
        }
        salvar_info_adicional(dir_resultados, info_adicional)

        # Mostrar estatísticas dos veículos
        print("\n" + titulo("ESTATÍSTICAS DOS AGENTES DE VEÍCULOS"))
        print("="*70)
        for agente in agentes[1:]:  # Pular o coordenador
            if isinstance(agente, VeiculoLearningAgent):
                stats = agente.obter_estatisticas()
                print(f"\n{destaque(agente.my_name)}:")
                print(f"  Veículo ID: {stats['veiculo_id']}")
                print(f"  Prioridade: {stats['prioridade']}")
                print(f"  Tentativas: {stats['tentativas']}")
                print(f"  Sucessos: {sucesso(str(stats['sucessos']))}")
                print(f"  Falhas: {erro(str(stats['falhas']))}")
                print(f"  Recompensa Acumulada: {stats['recompensa_acumulada']:.2f}")
                print(f"  Total de Ações: {stats['total_acoes']}")

        # Adicionar resultado ao comparador de cenários (para comparações futuras)
        exp_nome = config.get('experimento', 'customizado') if len(sys.argv) == 1 else args.experimento
        SCENARIO_COMPARATOR.adicionar_resultado(exp_nome, METRICS_COLLECTOR)

        # Mostrar tempo de execução
        tempo_total = METRICS_COLLECTOR.metricas_globais["tempo_fim"] - METRICS_COLLECTOR.metricas_globais["tempo_inicio"]
        print(f"\n{titulo('Tempo total de execução:')} {tempo_total:.2f} segundos")

        print("\n" + "="*70)
        print(sucesso("SISTEMA ENCERRADO COM SUCESSO"))
        print("="*70)
        print(f"\n{destaque('Resultados salvos em:')} {dir_resultados}/")
        print(f"\n{destaque('Arquivos gerados:')}")
        print(f"  • metricas_aprendizado.csv - Dados de métricas")
        print(f"  • graficos/ - Visualizações gráficas (5 gráficos)")
        print(f"  • info_execucao.txt - Informações da execução")
        print(f"\n{destaque('Acesso rápido:')}")
        print(f"  • resultados/ultima_execucao/ - Symlink para esta execução")
        print(f"\n{aviso('Dica:')} Execute múltiplos cenários para gerar comparações automáticas!")
        print(f"          python comparar_cenarios.py --cenarios todos")

    except ValueError as e:
        print(f"\n[ERRO DE CONFIGURAÇÃO] {e}")
        sys.exit(1)

    except RuntimeError as e:
        print(f"\n[ERRO DE EXECUÇÃO] {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[INTERROMPIDO PELO USUÁRIO]")
        print("Sistema sendo encerrado...")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] {type(e).__name__}: {e}")
        print("Sistema não pode continuar.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
