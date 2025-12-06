"""
Sistema Multi-Agentes de Negociação em Cruzamento com Aprendizado Q-Learning
Versão Modularizada - Imports from lib/

Trabalho 02 - Aprendizado - SMA 2025.2 - UTFPR
"""

from maspy import *
from maspy.learning import *
import argparse
import sys
import time

# Imports from modularized library
from lib import (
    # Config
    VEICULOS_CONFIG, EXPERIMENTOS, LogLevel, GLOBAL_LOG_LEVEL,
    # Utils
    Cores, cor, titulo, sucesso, erro, aviso, info, destaque,
    criar_diretorio_resultados, salvar_info_adicional,
    # Metrics
    MetricsCollector, ScenarioComparator,
    METRICS_COLLECTOR, SCENARIO_COMPARATOR,
    # Environment
    CruzamentoLearningEnvironment,
    # Agents
    LoggableAgent, CoordenadorLearningAgent, VeiculoLearningAgent,
)


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
        '--recompensa',
        type=int,
        default=100,
        help='Recompensa por escolha correta (padrão: 100)'
    )
    parser.add_argument(
        '--penalidade',
        type=float,
        default=1.0,
        help='Multiplicador de penalidade por escolha incorreta (padrão: 1.0)'
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
        for i, (nome, dados) in enumerate(EXPERIMENTOS.items(), 1):
            num_veiculos = len(dados["veiculos"])
            print(f"  {cor(f'{i:2d}', Cores.AMARELO)}. {nome:<25} - {dados['titulo']}")
            print(f"      {cor('Descrição:', Cores.CIANO)} {dados['descricao']}")
            print(f"      {cor('Veículos:', Cores.CIANO)} {num_veiculos}\n")

        while True:
            try:
                escolha_exp = input(cor(">>> Escolha o experimento (número): ", Cores.CIANO)).strip()
                idx = int(escolha_exp) - 1
                if 0 <= idx < len(opcoes):
                    nome_exp = opcoes[idx]
                    config["experimento"] = nome_exp
                    config["veiculos"] = EXPERIMENTOS[nome_exp]["veiculos"]
                    break
                print(erro("Número inválido!"))
            except (ValueError, KeyboardInterrupt):
                return None

    else:
        # Experimento customizado
        print("\n" + destaque("Configuração customizada:\n"))
        print("Escolha os veículos (separados por vírgula, ex: 1,3,5):\n")

        veiculos_base = VEICULOS_CONFIG
        for i, v in enumerate(veiculos_base, 1):
            print(f"  {i:2d}. {v['nome']:<15} - {v['tipo']:<12} (prioridade={v['prioridade']})")

        while True:
            try:
                escolha_veiculos = input(cor("\n>>> Veículos: ", Cores.CIANO)).strip()
                indices = [int(x.strip()) - 1 for x in escolha_veiculos.split(',')]
                if all(0 <= i < len(veiculos_base) for i in indices):
                    config["veiculos"] = [veiculos_base[i] for i in indices]
                    config["experimento"] = "customizado"
                    break
                print(erro("Números inválidos!"))
            except (ValueError, KeyboardInterrupt):
                return None

    # Configurar episódios
    print(f"\n{destaque('Número de episódios de treinamento')} (padrão: 100):")
    print(f"{aviso('Dica:')} Mais episódios = mais aprendizado (recomendado: 100-1000)")
    while True:
        try:
            episodios_input = input(cor(">>> Episódios: ", Cores.CIANO)).strip()
            if episodios_input == "":
                config["episodios"] = 100
                break
            ep = int(episodios_input)
            if ep > 0:
                config["episodios"] = ep
                break
            print(erro("Deve ser maior que 0!"))
        except (ValueError, KeyboardInterrupt):
            return None

    # Configurar log level
    print(f"\n{destaque('Nível de log')} (1=SILENT, 2=ERROR, 3=INFO, 4=DEBUG, padrão: INFO):")
    print(f"{aviso('Dica:')} INFO mostra progresso detalhado, SILENT oculta tudo")
    while True:
        try:
            log_input = input(cor(">>> Log Level: ", Cores.CIANO)).strip()
            if log_input == "":
                config["log_level"] = LogLevel.INFO
                break
            nivel = int(log_input)
            if 1 <= nivel <= 4:
                config["log_level"] = [LogLevel.SILENT, LogLevel.ERROR, LogLevel.INFO, LogLevel.DEBUG][nivel-1]
                break
            print(erro("Opção inválida!"))
        except (ValueError, KeyboardInterrupt):
            return None

    # Configurar recompensa
    print(f"\n{destaque('Recompensa por escolha correta')} (padrão: 100):")
    print(f"{aviso('Dica:')} Valores maiores incentivam mais a escolha correta")
    print(f"{aviso('Exemplos:')} 10 (baixa), 50 (média), 100 (alta), 200 (muito alta)")
    while True:
        try:
            recompensa_input = input(cor(">>> Recompensa: ", Cores.CIANO)).strip()
            if recompensa_input == "":
                config["recompensa"] = 100
                break
            rec = int(recompensa_input)
            if rec > 0:
                config["recompensa"] = rec
                break
            print(erro("Deve ser maior que 0!"))
        except (ValueError, KeyboardInterrupt):
            return None

    # Configurar penalidade
    print(f"\n{destaque('Multiplicador de penalidade')} (padrão: 1.0):")
    print(f"{aviso('Dica:')} Controla o quanto o agente é punido por erros")
    print(f"{aviso('Exemplos:')} 0.5 (leniente), 1.0 (balanceado), 2.0 (severo)")
    while True:
        try:
            penalidade_input = input(cor(">>> Penalidade: ", Cores.CIANO)).strip()
            if penalidade_input == "":
                config["penalidade"] = 1.0
                break
            pen = float(penalidade_input)
            if pen > 0:
                config["penalidade"] = pen
                break
            print(erro("Deve ser maior que 0!"))
        except (ValueError, KeyboardInterrupt):
            return None

    return config


if __name__ == "__main__":
    try:
        # RESETAR MÉTRICAS GLOBAIS (IMPORTANTE)
        METRICS_COLLECTOR.reset()

        # Determinar se foi chamado via linha de comando ou interativamente
        if len(sys.argv) > 1:
            # Modo CLI
            args = parse_arguments()

            # Converter log level string para enum
            log_level = LogLevel[args.log_level]

            # Obter configuração do experimento
            config = EXPERIMENTOS[args.experimento]["veiculos"]
            nome_experimento = args.experimento
            episodios = args.episodios
            recompensa_correta = args.recompensa
            penalidade_mult = args.penalidade
            verbose = not args.quiet

        else:
            # Modo interativo
            config_interactive = menu_interativo()
            if config_interactive is None:
                print("\n" + aviso("Execução cancelada pelo usuário."))
                sys.exit(0)

            config = config_interactive["veiculos"]
            nome_experimento = config_interactive.get("experimento", "customizado")
            episodios = config_interactive.get("episodios", 100)
            log_level = config_interactive.get("log_level", LogLevel.INFO)
            recompensa_correta = config_interactive.get("recompensa", 100)
            penalidade_mult = config_interactive.get("penalidade", 1.0)
            verbose = (log_level.value >= LogLevel.INFO.value)

        # Criar diretório de resultados com timestamp
        dir_resultados = criar_diretorio_resultados(nome_experimento)

        # Associar diretório ao coletor de métricas
        METRICS_COLLECTOR.dir_execucao = dir_resultados

        # Mostrar configuração
        imprimir_configuracao(config, log_level, episodios)

        # Configurar variáveis de classe do ambiente
        CruzamentoLearningEnvironment._veiculos_config_override = config
        CruzamentoLearningEnvironment._verbose = verbose
        CruzamentoLearningEnvironment._reward_correto = recompensa_correta
        CruzamentoLearningEnvironment._penalidade_multiplicador = penalidade_mult
        CruzamentoLearningEnvironment._step_by_step = False

        # Registrar início do treinamento
        METRICS_COLLECTOR.metricas_globais["tempo_inicio"] = time.time()

        # Criar ambiente
        env = CruzamentoLearningEnvironment()

        # Criar agente coordenador de aprendizado
        coordenador = CoordenadorLearningAgent(
            agt_name="Coordenador_QLearning",
            env=env,
            num_episodes=episodios,
            log_level=log_level
        )

        # Registrar agente no coletor de métricas
        METRICS_COLLECTOR.registrar_agente(coordenador.my_name)

        # Executar sistema
        print("\n" + titulo("INICIANDO SISTEMA MULTI-AGENTES"))
        print("="*70 + "\n")

        Admin().start_system()

        # Registrar fim do treinamento
        METRICS_COLLECTOR.metricas_globais["tempo_fim"] = time.time()

        print("\n" + titulo("SISTEMA FINALIZADO"))
        print("="*70 + "\n")

        # Gerar relatório de métricas
        relatorio = METRICS_COLLECTOR.gerar_relatorio()
        print(relatorio)

        # Exportar para CSV
        METRICS_COLLECTOR.exportar_csv()

        # Gerar gráficos
        METRICS_COLLECTOR.gerar_graficos()

        # Salvar informações adicionais da execução
        salvar_info_adicional(dir_resultados, {
            "Experimento": nome_experimento,
            "Número de veículos": len(config),
            "Episódios de treinamento": episodios,
            "Recompensa por escolha correta": recompensa_correta,
            "Multiplicador de penalidade": penalidade_mult,
            "Log level": log_level.name,
        })

        # Adicionar resultado ao comparador de cenários (para comparações futuras)
        exp_nome = nome_experimento
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
