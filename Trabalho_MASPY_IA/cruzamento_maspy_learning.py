"""
Sistema Multi-Agentes de Negociacao em Cruzamento com Aprendizado Q-Learning
Versao Modularizada - Imports from lib/


Fluxo Multi-Agente:
1. Cria CruzamentoLearningEnvironment
2. Cria CoordenadorLearningAgent
3. Cria VeiculoLearningAgent para CADA veiculo da config
4. Cria Channel() e Channel("comunicacao")
5. admin.connect_to([coordenador, *veiculos], [env, canal, canal_comunicacao])
6. admin.start_system()
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
        description="Sistema Multi-Agentes de Negociacao em Cruzamento com Aprendizado Q-Learning"
    )
    parser.add_argument(
        '--log-level',
        choices=['SILENT', 'ERROR', 'INFO', 'DEBUG'],
        default='INFO',
        help='Nivel de log (padrao: INFO)'
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
        help='Numero de episodios para treinamento Q-Learning (padrao: 100)'
    )
    parser.add_argument(
        '--recompensa',
        type=int,
        default=100,
        help='Recompensa por escolha correta (padrao: 100)'
    )
    parser.add_argument(
        '--penalidade',
        type=float,
        default=1.0,
        help='Multiplicador de penalidade por escolha incorreta (padrao: 1.0)'
    )
    parser.add_argument(
        '--simulacoes',
        type=int,
        default=20,
        help='Numero de episodios de simulacao pos-treinamento (padrao: 20)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Esconder logs detalhados do aprendizado'
    )
    return parser.parse_args()


def imprimir_configuracao(config, log_level, episodios=100):
    """Imprime a configuracao do sistema."""
    print("="*70)
    print("SISTEMA MULTI-AGENTES - APRENDIZADO Q-LEARNING")
    print("="*70)

    print("\nConfiguracao do Sistema:")
    print(f"  - {len(config)} Veiculos")
    print(f"  - Log Level: {log_level.name}")
    print(f"  - Episodios Q-Learning: {episodios}")

    print("\n  Veiculos:")
    for v in config:
        emergencia = " [EMERGENCIA]" if v["prioridade"] >= 100 else ""
        print(f"    - {v['nome']}: {v['tipo']} (prioridade={v['prioridade']}){emergencia}")

    print("\n  Aprendizado por Reforco (Q-Learning):")
    print("    1. Coordenador treina Q-Learning (explora estados e acoes)")
    print("    2. Recebe recompensas (+100 prioridade correta, -penalidade proporcional)")
    print("    3. Atualiza Q-table com experiencias")
    print("    4. Apos treinamento, coordena veiculos via comunicacao multi-agente")

    print("\n  Comunicacao Multi-Agente:")
    print("    5. Coordenador solicita propostas dos veiculos (send/tell)")
    print("    6. Veiculos enviam propostas ao coordenador")
    print("    7. Coordenador decide ordem com politica aprendida")
    print("    8. Veiculos recebem decisoes e ordem final")

    print("\n" + "="*70 + "\n")


def menu_interativo():
    """Interface interativa colorida para configurar o experimento."""
    print("\n" + titulo("="*70))
    print(titulo("  SISTEMA MULTI-AGENTES - APRENDIZADO Q-LEARNING"))
    print(titulo("="*70) + "\n")

    # Escolher tipo de experimento
    print(destaque("Escolha o tipo de experimento:\n"))
    print(f"  {cor('1', Cores.AMARELO)}. Experimento pre-definido")
    print(f"  {cor('2', Cores.AMARELO)}. Experimento customizado")
    print(f"  {cor('0', Cores.VERMELHO)}. Sair\n")

    while True:
        try:
            escolha = input(cor(">>> Opcao: ", Cores.CIANO)).strip()
            if escolha == "0":
                return None
            if escolha in ["1", "2"]:
                break
            print(erro("Opcao invalida!"))
        except KeyboardInterrupt:
            return None

    config = {}

    if escolha == "1":
        # Experimento pre-definido
        print("\n" + destaque("Experimentos disponiveis:\n"))
        opcoes = list(EXPERIMENTOS.keys())
        for i, (nome, dados) in enumerate(EXPERIMENTOS.items(), 1):
            num_veiculos = len(dados["veiculos"])
            print(f"  {cor(f'{i:2d}', Cores.AMARELO)}. {nome:<25} - {dados['titulo']}")
            print(f"      {cor('Descricao:', Cores.CIANO)} {dados['descricao']}")
            print(f"      {cor('Veiculos:', Cores.CIANO)} {num_veiculos}\n")

        while True:
            try:
                escolha_exp = input(cor(">>> Escolha o experimento (numero): ", Cores.CIANO)).strip()
                idx = int(escolha_exp) - 1
                if 0 <= idx < len(opcoes):
                    nome_exp = opcoes[idx]
                    config["experimento"] = nome_exp
                    config["veiculos"] = EXPERIMENTOS[nome_exp]["veiculos"]
                    break
                print(erro("Numero invalido!"))
            except (ValueError, KeyboardInterrupt):
                return None

    else:
        # Experimento customizado
        print("\n" + destaque("Configuracao customizada:\n"))
        print("Escolha os veiculos (separados por virgula, ex: 1,3,5):\n")

        veiculos_base = VEICULOS_CONFIG
        for i, v in enumerate(veiculos_base, 1):
            print(f"  {i:2d}. {v['nome']:<15} - {v['tipo']:<12} (prioridade={v['prioridade']})")

        while True:
            try:
                escolha_veiculos = input(cor("\n>>> Veiculos: ", Cores.CIANO)).strip()
                indices = [int(x.strip()) - 1 for x in escolha_veiculos.split(',')]
                if all(0 <= i < len(veiculos_base) for i in indices):
                    config["veiculos"] = [veiculos_base[i] for i in indices]
                    config["experimento"] = "customizado"
                    break
                print(erro("Numeros invalidos!"))
            except (ValueError, KeyboardInterrupt):
                return None

    # Configurar episodios
    print(f"\n{destaque('Numero de episodios de treinamento')} (padrao: 100):")
    print(f"{aviso('Dica:')} Mais episodios = mais aprendizado (recomendado: 100-1000)")
    while True:
        try:
            episodios_input = input(cor(">>> Episodios: ", Cores.CIANO)).strip()
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
    print(f"\n{destaque('Nivel de log')} (1=SILENT, 2=ERROR, 3=INFO, 4=DEBUG, padrao: INFO):")
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
            print(erro("Opcao invalida!"))
        except (ValueError, KeyboardInterrupt):
            return None

    # Configurar recompensa
    print(f"\n{destaque('Recompensa por escolha correta')} (padrao: 100):")
    print(f"{aviso('Dica:')} Valores maiores incentivam mais a escolha correta")
    print(f"{aviso('Exemplos:')} 10 (baixa), 50 (media), 100 (alta), 200 (muito alta)")
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
    print(f"\n{destaque('Multiplicador de penalidade')} (padrao: 1.0):")
    print(f"{aviso('Dica:')} Controla o quanto o agente e punido por erros")
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
        # RESETAR METRICAS GLOBAIS (IMPORTANTE)
        METRICS_COLLECTOR.reset()

        # Determinar se foi chamado via linha de comando ou interativamente
        if len(sys.argv) > 1:
            # Modo CLI
            args = parse_arguments()

            # Converter log level string para enum
            log_level = LogLevel[args.log_level]

            # Obter configuracao do experimento
            config = EXPERIMENTOS[args.experimento]["veiculos"]
            nome_experimento = args.experimento
            episodios = args.episodios
            simulacoes = args.simulacoes
            recompensa_correta = args.recompensa
            penalidade_mult = args.penalidade
            verbose = not args.quiet

        else:
            # Modo interativo
            config_interactive = menu_interativo()
            if config_interactive is None:
                print("\n" + aviso("Execucao cancelada pelo usuario."))
                sys.exit(0)

            config = config_interactive["veiculos"]
            nome_experimento = config_interactive.get("experimento", "customizado")
            episodios = config_interactive.get("episodios", 100)
            simulacoes = 20
            log_level = config_interactive.get("log_level", LogLevel.INFO)
            recompensa_correta = config_interactive.get("recompensa", 100)
            penalidade_mult = config_interactive.get("penalidade", 1.0)
            verbose = (log_level.value >= LogLevel.INFO.value)

        # Criar diretorio de resultados com timestamp
        dir_resultados = criar_diretorio_resultados(nome_experimento)

        # Associar diretorio ao coletor de metricas
        METRICS_COLLECTOR.dir_execucao = dir_resultados

        # Mostrar configuracao
        imprimir_configuracao(config, log_level, episodios)

        # Configurar variaveis de classe do ambiente
        CruzamentoLearningEnvironment._veiculos_config_override = config
        CruzamentoLearningEnvironment._verbose = verbose
        CruzamentoLearningEnvironment._reward_correto = recompensa_correta
        CruzamentoLearningEnvironment._penalidade_multiplicador = penalidade_mult
        CruzamentoLearningEnvironment._step_by_step = False

        # Registrar inicio do treinamento
        METRICS_COLLECTOR.metricas_globais["tempo_inicio"] = time.time()

        # ========================================
        # CRIAR INFRAESTRUTURA MULTI-AGENTE
        # ========================================

        # 1. Criar ambiente
        env = CruzamentoLearningEnvironment()

        # 2. Criar agente coordenador de aprendizado
        coordenador = CoordenadorLearningAgent(
            agt_name="Coordenador_QLearning",
            env=env,
            num_episodes=episodios,
            num_simulacoes=simulacoes,
            log_level=log_level
        )

        # Registrar agente no coletor de metricas
        METRICS_COLLECTOR.registrar_agente(coordenador.my_name)

        # 3. Criar VeiculoLearningAgent para CADA veiculo da config
        # Usa os nomes internos (Veiculo1, Veiculo2, ...) para consistencia com o ambiente
        veiculos = []
        for i, v_config in enumerate(config):
            veiculo_id = f"Veiculo{i+1}"  # Nome interno do ambiente
            veiculo = VeiculoLearningAgent(
                agt_name=f"Agente_{v_config['nome']}",
                veiculo_id=veiculo_id,
                prioridade=v_config["prioridade"],
                tipo=v_config["tipo"],
                log_level=log_level
            )
            veiculos.append(veiculo)

        print(f"\n{sucesso('Agentes criados:')}")
        print(f"  Coordenador: {coordenador.my_name}")
        for v in veiculos:
            print(f"  Veiculo: {v.my_name} (id={v.veiculo_id}, prio={v.prioridade}, tipo={v.tipo})")
        print(f"\n  Total: 1 coordenador + {len(veiculos)} veiculos = {1 + len(veiculos)} agentes\n")

        # 4. Criar canais de comunicacao
        canal_default = Channel()                  # Canal padrao
        canal_comunicacao = Channel("comunicacao")  # Canal dedicado inter-agente

        print(f"{sucesso('Canais criados:')} default, comunicacao")

        # 5. Conectar tudo via MASPY: agentes -> [ambiente, canais]
        todos_agentes = [coordenador] + veiculos
        admin = Admin()
        admin.connect_to(todos_agentes, [env, canal_default, canal_comunicacao])

        print(f"{sucesso('Conexao estabelecida:')} {len(todos_agentes)} agentes -> ambiente + 2 canais\n")

        # Executar sistema
        print("\n" + titulo("INICIANDO SISTEMA MULTI-AGENTES"))
        print("="*70 + "\n")

        admin.start_system()

        # Registrar fim do treinamento
        METRICS_COLLECTOR.metricas_globais["tempo_fim"] = time.time()

        print("\n" + titulo("SISTEMA FINALIZADO"))
        print("="*70 + "\n")

        # ========================================
        # RELATORIO POS-EXECUCAO DETALHADO
        # ========================================

        # 1) PARAMETROS Q-LEARNING
        print(titulo("="*70))
        print(titulo("  PARAMETROS DO Q-LEARNING"))
        print(titulo("="*70))
        ql = coordenador.ql_params
        print(f"  Alpha (taxa de aprendizado):   {ql['alpha']}")
        print(f"  Gamma (fator de desconto):     {ql['gamma']}")
        print(f"  Epsilon inicial:               {ql['epsilon_inicial']}")
        print(f"  Epsilon decay:                 {ql['epsilon_decay']}")
        print(f"  Epsilon minimo:                {ql['epsilon_min']}")
        if coordenador.epsilon_final is not None:
            print(f"  Epsilon final (apos treino):   {coordenador.epsilon_final:.6f}")
        print(f"  Episodios de treinamento:      {episodios}")
        print(f"  Recompensa por acerto:         +{recompensa_correta}")
        print(f"  Multiplicador de penalidade:   {penalidade_mult}x")
        print()

        # 2) ORDEM APRENDIDA vs ORDEM OTIMA
        print(titulo("="*70))
        print(titulo("  ORDEM APRENDIDA vs ORDEM OTIMA"))
        print(titulo("="*70))

        # Ordem otima: veiculos ordenados por prioridade decrescente
        ordem_otima = sorted(
            env.veiculos_ids,
            key=lambda v: env.prioridades[v],
            reverse=True
        )
        ordem_aprendida = coordenador.ordem_aprendida

        # Calcular acertos de posicao
        acertos_posicao = 0
        total_posicoes = len(ordem_otima)

        print(f"\n  {'Pos':<5} {'Otima (por prioridade)':<30} {'Aprendida (Q-table)':<30} {'Status':<10}")
        print(f"  {'-'*5} {'-'*30} {'-'*30} {'-'*10}")
        for i in range(total_posicoes):
            v_otimo = ordem_otima[i] if i < len(ordem_otima) else "?"
            v_aprendido = ordem_aprendida[i] if i < len(ordem_aprendida) else "?"

            nome_otimo = env.nomes_originais.get(v_otimo, v_otimo)
            prio_otimo = env.prioridades.get(v_otimo, 0)
            nome_aprendido = env.nomes_originais.get(v_aprendido, v_aprendido)
            prio_aprendido = env.prioridades.get(v_aprendido, 0)

            # Considerar correto se a prioridade bate (empates sao validos)
            match = prio_aprendido == prio_otimo
            if match:
                acertos_posicao += 1
            status = sucesso("OK") if match else erro("DIFF")

            print(f"  {i+1:<5} {nome_otimo} (prio={prio_otimo}){'':<{18-len(nome_otimo)}} "
                  f"{nome_aprendido} (prio={prio_aprendido}){'':<{18-len(nome_aprendido)}} "
                  f"{status}")

        taxa_posicao = acertos_posicao / total_posicoes * 100 if total_posicoes > 0 else 0
        print(f"\n  Precisao de posicao: {acertos_posicao}/{total_posicoes} ({taxa_posicao:.1f}%)")
        if taxa_posicao == 100:
            print(f"  {sucesso('A politica aprendida replica perfeitamente a ordem otima!')}")
        elif taxa_posicao >= 80:
            print(f"  {aviso('A politica esta proxima da otima. Mais episodios podem melhorar.')}")
        else:
            print(f"  {erro('A politica diverge da otima. Considere aumentar episodios ou ajustar parametros.')}")
        print()

        # 3) TABELA POR VEICULO (posicao recebida vs esperada)
        print(titulo("="*70))
        print(titulo("  RESULTADO POR VEICULO (COORDENACAO MULTI-AGENTE)"))
        print(titulo("="*70))

        print(f"\n  {'Agente':<25} {'Tipo':<12} {'Prio':<6} {'Pos Recebida':<14} {'Pos Esperada':<14} {'Status':<10}")
        print(f"  {'-'*25} {'-'*12} {'-'*6} {'-'*14} {'-'*14} {'-'*10}")
        for v in veiculos:
            # Posicao esperada = posicao na ordem otima (por prioridade)
            pos_esperada = None
            for idx, v_otimo in enumerate(ordem_otima):
                if env.prioridades.get(v_otimo, 0) == v.prioridade:
                    # Encontrar a primeira posicao com essa prioridade que ainda nao foi atribuida
                    pos_esperada = idx + 1
                    break
            if pos_esperada is None:
                pos_esperada = "?"

            pos_recebida = v.posicao_recebida if v.posicao_recebida else "-"
            match = (isinstance(pos_recebida, int) and isinstance(pos_esperada, int)
                     and pos_recebida == pos_esperada)
            # Considerar match se prioridade na posicao recebida bate com prioridade na posicao esperada
            if isinstance(pos_recebida, int) and pos_recebida <= len(ordem_aprendida):
                vid_recebido = ordem_aprendida[pos_recebida - 1]
                prio_na_pos_recebida = env.prioridades.get(vid_recebido, 0)
                prio_esperada = env.prioridades.get(ordem_otima[pos_recebida - 1], 0) if pos_recebida <= len(ordem_otima) else 0
                match_prio = (prio_na_pos_recebida == prio_esperada)
            else:
                match_prio = False

            status = sucesso("OK") if match_prio else (aviso("~") if isinstance(pos_recebida, int) else "-")

            print(f"  {v.my_name:<25} {v.tipo:<12} {v.prioridade:<6} {str(pos_recebida):<14} {str(pos_esperada):<14} {status}")
        print()

        # 4) RESUMO DA COMUNICACAO MULTI-AGENTE
        print(titulo("="*70))
        print(titulo("  COMUNICACAO MULTI-AGENTE"))
        print(titulo("="*70))

        coord_stats = coordenador.comm_stats
        total_msgs_veiculos_env = sum(v.comm_stats["mensagens_enviadas"] for v in veiculos)
        total_msgs_veiculos_rec = sum(v.comm_stats["mensagens_recebidas"] for v in veiculos)
        total_msgs_sistema = coord_stats["mensagens_enviadas"] + total_msgs_veiculos_env

        print(f"\n  {destaque('Coordenador')} ({coordenador.my_name}):")
        print(f"    Mensagens enviadas:     {coord_stats['mensagens_enviadas']}")
        print(f"      - Solicitacoes:       {coord_stats['solicitacoes_enviadas']}")
        print(f"      - Decisoes:           {coord_stats['decisoes_enviadas']}")
        print(f"      - Ordens completas:   {coord_stats['ordens_enviadas']}")
        print(f"    Mensagens recebidas:    {coord_stats['mensagens_recebidas']}")
        print(f"      - Propostas:          {coord_stats['propostas_recebidas']}")

        print(f"\n  {destaque('Veiculos')} ({len(veiculos)} agentes):")
        print(f"    Total enviadas:         {total_msgs_veiculos_env}")
        print(f"    Total recebidas:        {total_msgs_veiculos_rec}")
        print(f"    Media por veiculo:      {total_msgs_veiculos_env/len(veiculos):.1f} env, {total_msgs_veiculos_rec/len(veiculos):.1f} rec")

        print(f"\n  {destaque('Total do sistema:')}          {total_msgs_sistema} mensagens")
        print(f"  Canal utilizado:            \"{coord_stats['canal_utilizado']}\"")
        print(f"  Protocolo:                  send/tell via Belief")
        print(f"  Descoberta de agentes:      list_agents()")
        print()

        # 5) Q-TABLE: TOP ENTRADAS
        print(titulo("="*70))
        print(titulo("  Q-TABLE: TOP ENTRADAS (ESTADO INICIAL)"))
        print(titulo("="*70))

        # Mostrar Q-values para o estado inicial (todos veiculos disponiveis)
        estado_inicial = env.possible_starts.copy()
        estado_tupla_inicial = coordenador.estado_para_tupla(estado_inicial)

        q_estado_inicial = {}
        for v in env.veiculos_ids:
            q_val = coordenador.q_table.get((estado_tupla_inicial, v), 0.0)
            q_estado_inicial[v] = q_val

        q_sorted = sorted(q_estado_inicial.items(), key=lambda x: x[1], reverse=True)

        print(f"\n  Estado: todos os veiculos disponiveis (estado inicial)")
        print(f"\n  {'Veiculo':<15} {'Nome Original':<18} {'Prio':<6} {'Q-Value':<12} {'Rank':<5}")
        print(f"  {'-'*15} {'-'*18} {'-'*6} {'-'*12} {'-'*5}")
        for rank, (vid, qval) in enumerate(q_sorted, 1):
            nome_orig = env.nomes_originais.get(vid, vid)
            prio = env.prioridades.get(vid, 0)
            print(f"  {vid:<15} {nome_orig:<18} {prio:<6} {qval:<12.4f} {rank}")

        # Stats da Q-table
        total_entries = len(coordenador.q_table)
        non_zero = sum(1 for v in coordenador.q_table.values() if v != 0.0)
        max_q = max(coordenador.q_table.values()) if coordenador.q_table else 0
        min_q = min(coordenador.q_table.values()) if coordenador.q_table else 0

        print(f"\n  {destaque('Estatisticas da Q-Table:')}")
        print(f"    Entradas totais:       {total_entries}")
        print(f"    Entradas nao-zero:     {non_zero}")
        print(f"    Q-value maximo:        {max_q:.4f}")
        print(f"    Q-value minimo:        {min_q:.4f}")
        print()

        # ========================================
        # RELATORIO DE METRICAS ORIGINAL
        # ========================================

        # Gerar relatorio de metricas
        relatorio = METRICS_COLLECTOR.gerar_relatorio()
        print(relatorio)

        # Exportar para CSV
        METRICS_COLLECTOR.exportar_csv()

        # Gerar graficos
        METRICS_COLLECTOR.gerar_graficos()

        # Salvar informacoes adicionais da execucao
        salvar_info_adicional(dir_resultados, {
            "Experimento": nome_experimento,
            "Numero de veiculos": len(config),
            "Numero de agentes": 1 + len(config),
            "Episodios de treinamento": episodios,
            "Recompensa por escolha correta": recompensa_correta,
            "Multiplicador de penalidade": penalidade_mult,
            "Log level": log_level.name,
            "Canais de comunicacao": "default, comunicacao",
            "Alpha": ql["alpha"],
            "Gamma": ql["gamma"],
            "Epsilon inicial": ql["epsilon_inicial"],
            "Epsilon decay": ql["epsilon_decay"],
            "Epsilon min": ql["epsilon_min"],
            "Epsilon final": f"{coordenador.epsilon_final:.6f}" if coordenador.epsilon_final else "N/A",
            "Q-Table entradas": total_entries,
            "Q-Table entradas nao-zero": non_zero,
            "Total mensagens multi-agente": total_msgs_sistema,
            "Precisao ordem aprendida": f"{taxa_posicao:.1f}%",
        })

        # Adicionar resultado ao comparador de cenarios
        exp_nome = nome_experimento
        SCENARIO_COMPARATOR.adicionar_resultado(exp_nome, METRICS_COLLECTOR)

        # Mostrar tempo de execucao
        tempo_total = METRICS_COLLECTOR.metricas_globais["tempo_fim"] - METRICS_COLLECTOR.metricas_globais["tempo_inicio"]
        print(f"\n{titulo('Tempo total de execucao:')} {tempo_total:.2f} segundos")

        print("\n" + "="*70)
        print(sucesso("SISTEMA ENCERRADO COM SUCESSO"))
        print("="*70)
        print(f"\n{destaque('Resultados salvos em:')} {dir_resultados}/")
        print(f"\n{destaque('Arquivos gerados:')}")
        print(f"  - metricas_aprendizado.csv - Dados de metricas")
        print(f"  - graficos/ - Visualizacoes graficas (5 graficos)")
        print(f"  - info_execucao.txt - Informacoes da execucao")
        print(f"\n{destaque('Acesso rapido:')}")
        print(f"  - resultados/ultima_execucao/ - Symlink para esta execucao")
        print(f"\n{aviso('Dica:')} Execute multiplos cenarios para gerar comparacoes automaticas!")

    except ValueError as e:
        print(f"\n[ERRO DE CONFIGURACAO] {e}")
        sys.exit(1)

    except RuntimeError as e:
        print(f"\n[ERRO DE EXECUCAO] {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[INTERROMPIDO PELO USUARIO]")
        print("Sistema sendo encerrado...")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERRO CRITICO] {type(e).__name__}: {e}")
        print("Sistema nao pode continuar.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
