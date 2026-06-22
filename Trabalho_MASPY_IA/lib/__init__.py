"""
MASPY Learning - Modularized Package
Sistema Multi-Agentes com Q-Learning para Cruzamento
"""

from .config import VEICULOS_CONFIG, EXPERIMENTOS, LogLevel, GLOBAL_LOG_LEVEL
from .utils import (
    Cores, cor, titulo, sucesso, erro, aviso, info, destaque,
    criar_diretorio_resultados, salvar_info_adicional, signal_handler
)
from .metrics import (
    MetricsCollector, ScenarioComparator,
    METRICS_COLLECTOR, SCENARIO_COMPARATOR
)
from .environment import CruzamentoLearningEnvironment
from .agents import LoggableAgent, CoordenadorLearningAgent, VeiculoLearningAgent

__all__ = [
    # Config
    'VEICULOS_CONFIG', 'EXPERIMENTOS', 'LogLevel', 'GLOBAL_LOG_LEVEL',
    # Utils
    'Cores', 'cor', 'titulo', 'sucesso', 'erro', 'aviso', 'info', 'destaque',
    'criar_diretorio_resultados', 'salvar_info_adicional', 'signal_handler',
    # Metrics
    'MetricsCollector', 'ScenarioComparator',
    'METRICS_COLLECTOR', 'SCENARIO_COMPARATOR',
    # Environment
    'CruzamentoLearningEnvironment',
    # Agents
    'LoggableAgent', 'CoordenadorLearningAgent', 'VeiculoLearningAgent',
]
