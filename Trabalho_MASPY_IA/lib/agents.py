"""
Agentes para Sistema de Aprendizado Multi-Agente
Implementa comunicacao inter-agente via MASPY (send/tell/Belief)
com Q-Learning para ordenacao de veiculos.

Fluxo:
1. Coordenador treina Q-Learning (Goal "aprender")
2. Coordenador inicia coordenacao multi-agente (Goal "coordenar_travessia")
3. Veiculos enviam propostas ao coordenador
4. Coordenador decide ordem com politica aprendida
5. Veiculos recebem decisoes e atualizam status
"""

import sys
import random
import time
from collections import defaultdict
from maspy import *
from maspy.learning import *
from maspy.agent import *

from .config import GLOBAL_LOG_LEVEL, LogLevel
from .environment import CruzamentoLearningEnvironment
from .metrics import METRICS_COLLECTOR


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



# AGENTE COORDENADOR DE APRENDIZADO

class CoordenadorLearningAgent(LoggableAgent):
    """
    Agente coordenador que usa Q-Learning para aprender
    a ordem otima de travessia dos veiculos.

    Fase 1 (Goal "aprender"): Treina Q-Learning manualmente com metricas
    Fase 2 (Goal "coordenar_travessia"): Coordena veiculos via comunicacao
        multi-agente, usando a Q-table aprendida para decidir a ordem.
    """

    def __init__(self, agt_name=None, env=None, num_episodes=100, num_simulacoes=20, log_level=None):
        super().__init__(agt_name, log_level)

        self.env = env
        self.num_episodes = num_episodes
        self.num_simulacoes = num_simulacoes
        self.q_table = defaultdict(float)

        # Estado da coordenacao multi-agente
        self.propostas_recebidas = []
        self.num_veiculos_esperados = 0
        self.ordem_aprendida = []

        # Parametros Q-Learning (expostos para relatorio pos-execucao)
        self.ql_params = {
            "alpha": 0.1,
            "gamma": 0.9,
            "epsilon_inicial": 1.0,
            "epsilon_decay": 0.995,
            "epsilon_min": 0.01,
        }
        self.epsilon_final = None  # valor final apos treinamento

        # Contadores de comunicacao multi-agente
        self.comm_stats = {
            "mensagens_enviadas": 0,
            "mensagens_recebidas": 0,
            "propostas_recebidas": 0,
            "decisoes_enviadas": 0,
            "ordens_enviadas": 0,
            "solicitacoes_enviadas": 0,
            "canal_utilizado": "comunicacao",
        }

        # Beliefs observaveis
        self.add(Belief("status", "inicializando"))
        self.add(Belief("episodio_atual", 0))
        self.add(Belief("recompensa_total", 0))

        # Goal para iniciar aprendizado
        self.add(Goal("aprender"))

    def _update_status(self, new_status):
        """Atualiza o status observavel do agente."""
        old_belief = self.get(Belief("status", Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief("status", new_status))

    def _update_belief(self, belief_name, value):
        """Atualiza um belief observavel."""
        old_belief = self.get(Belief(belief_name, Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief(belief_name, value))

    def estado_para_tupla(self, estado_dict):
        """Converte estado dict para tupla ordenada (hashable)."""
        env = self.env
        return tuple(estado_dict[env.veiculo_map[v]] for v in env.veiculos_ids)

    def escolher_acao_epsilon_greedy(self, estado_tupla, veiculos_disponiveis, epsilon):
        """Escolhe acao usando estrategia epsilon-greedy."""
        if random.random() < epsilon:
            return random.choice(veiculos_disponiveis)
        else:
            q_values = {v: self.q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
            max_q = max(q_values.values())
            melhores = [v for v, q in q_values.items() if q == max_q]
            return random.choice(melhores)

    @pl(gain, Goal("aprender"))
    def iniciar_aprendizado(self, src):
        """
        Inicia o processo de aprendizado por Q-Learning.
        Coleta metricas durante o processo de aprendizado.
        Ao terminar, dispara Goal("coordenar_travessia").
        """
        self._update_status("aprendendo")
        self.info_print("\n" + "="*60)
        self.info_print("INICIANDO APRENDIZADO POR Q-LEARNING")
        self.info_print("="*60)

        try:
            env = self.env
            self.info_print(f"Ambiente: {env.my_name}")

            # Criar modelo do ambiente (exploracao inicial)
            self.info_print("Criando modelo do ambiente (exploracao inicial)...")
            model = EnvModel(env)

            self.info_print(f"Treinando com {self.num_episodes} episodios...")
            self.info_print("-"*60)

            # Ativar flag de treinamento
            CruzamentoLearningEnvironment._em_treinamento = True
            CruzamentoLearningEnvironment._episodio_atual = 0

            recompensas_por_episodio = []

            self.info_print("\nExecutando treinamento com coleta de metricas...")

            # Parametros Q-Learning
            alpha = self.ql_params["alpha"]
            gamma = self.ql_params["gamma"]
            epsilon = self.ql_params["epsilon_inicial"]
            epsilon_decay = self.ql_params["epsilon_decay"]
            epsilon_min = self.ql_params["epsilon_min"]

            # Resetar Q-table
            self.q_table = defaultdict(float)
            q_table = self.q_table

            # Treinar por num_episodes episodios
            for ep in range(self.num_episodes):
                estado = env.possible_starts.copy()
                estado_tupla = self.estado_para_tupla(estado)
                recompensa_total = 0
                acoes_corretas = 0
                acoes_total = 0

                while True:
                    veiculos_disponiveis = [
                        v for v in env.veiculos_ids
                        if estado[env.veiculo_map[v]] == 0
                    ]

                    if not veiculos_disponiveis:
                        break

                    veiculo_escolhido = self.escolher_acao_epsilon_greedy(
                        estado_tupla, veiculos_disponiveis, epsilon
                    )

                    novo_estado, recompensa, terminado = env.transicao_escolher(
                        estado, veiculo_escolhido
                    )
                    novo_estado_tupla = self.estado_para_tupla(novo_estado)

                    melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
                    escolha_correta = (env.prioridades[veiculo_escolhido] == melhor_prioridade)
                    if escolha_correta:
                        acoes_corretas += 1
                    acoes_total += 1

                    # Bellman equation
                    if terminado:
                        target = recompensa
                    else:
                        proximos_disponiveis = [
                            v for v in env.veiculos_ids
                            if novo_estado[env.veiculo_map[v]] == 0
                        ]
                        max_q_proximo = max(
                            q_table[(novo_estado_tupla, v)] for v in proximos_disponiveis
                        ) if proximos_disponiveis else 0
                        target = recompensa + gamma * max_q_proximo

                    q_atual = q_table[(estado_tupla, veiculo_escolhido)]
                    q_table[(estado_tupla, veiculo_escolhido)] = q_atual + alpha * (target - q_atual)

                    recompensa_total += recompensa
                    estado = novo_estado
                    estado_tupla = novo_estado_tupla

                    if terminado:
                        break

                recompensas_por_episodio.append(recompensa_total)
                METRICS_COLLECTOR.adicionar_recompensa_episodio(
                    self.my_name, ep + 1, recompensa_total
                )

                for _ in range(acoes_corretas):
                    METRICS_COLLECTOR.registrar_acao(self.my_name, True)
                for _ in range(acoes_total - acoes_corretas):
                    METRICS_COLLECTOR.registrar_acao(self.my_name, False)

                epsilon = max(epsilon_min, epsilon * epsilon_decay)

                if (ep + 1) % 10 == 0:
                    if METRICS_COLLECTOR.verificar_convergencia(self.my_name, janela=10):
                        self.info_print(f"Convergencia detectada no episodio {ep + 1}!")

            self.epsilon_final = epsilon
            self.info_print(f"Treinamento concluido com {self.num_episodes} episodios.")
            self.info_print(f"Epsilon final: {epsilon:.6f}")

            CruzamentoLearningEnvironment._em_treinamento = False

            self.info_print("-"*60)
            self.info_print("TREINAMENTO CONCLUIDO!")

            # ========================================
            # FASE DE VALIDACAO
            # ========================================
            self.info_print("-"*60)
            self.info_print("INICIANDO VALIDACAO COM POLITICA APRENDIDA...")

            num_episodios_validacao = min(10, max(5, self.num_episodes // 10))
            acertos_validacao = 0
            total_acoes_validacao = 0
            recompensa_total_validacao = 0

            for ep_val in range(num_episodios_validacao):
                estado = env.possible_starts.copy()

                while True:
                    estado_tupla = self.estado_para_tupla(estado)
                    veiculos_disponiveis = [v for v in env.veiculos_ids
                                          if estado[env.veiculo_map[v]] == 0]

                    if not veiculos_disponiveis:
                        break

                    q_values = {v: q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
                    veiculo_escolhido = max(q_values, key=q_values.get)

                    novo_estado, recompensa, terminado = env.transicao_escolher(estado, veiculo_escolhido)
                    recompensa_total_validacao += recompensa
                    total_acoes_validacao += 1

                    if recompensa > 0:
                        acertos_validacao += 1

                    estado = novo_estado

                    if terminado:
                        break

            taxa_acerto_validacao = (acertos_validacao / total_acoes_validacao * 100) if total_acoes_validacao > 0 else 0
            recompensa_media_validacao = recompensa_total_validacao / num_episodios_validacao if num_episodios_validacao > 0 else 0

            self.info_print(f"Validacao concluida: {num_episodios_validacao} episodios")
            self.info_print(f"Taxa de acerto (validacao): {taxa_acerto_validacao:.2f}%")
            self.info_print(f"Recompensa media (validacao): {recompensa_media_validacao:.2f}")

            # ========================================
            # EXTRAIR ORDEM OTIMA DA Q-TABLE
            # ========================================
            self.ordem_aprendida = []
            estado_temp = env.possible_starts.copy()

            while len(self.ordem_aprendida) < len(env.veiculos_ids):
                estado_tupla_temp = self.estado_para_tupla(estado_temp)
                disponiveis = [v for v in env.veiculos_ids
                             if estado_temp[env.veiculo_map[v]] == 0]

                if not disponiveis:
                    break

                q_values_temp = {v: q_table[(estado_tupla_temp, v)] for v in disponiveis}
                melhor_veiculo = max(q_values_temp, key=q_values_temp.get)

                self.ordem_aprendida.append(melhor_veiculo)
                estado_temp[env.veiculo_map[melhor_veiculo]] = 1

            print("\n" + "="*50, flush=True)
            print("RESULTADO DO APRENDIZADO", flush=True)
            print("="*50, flush=True)

            print(f"\nOrdem otima aprendida (via Q-table): {' -> '.join(self.ordem_aprendida)}", flush=True)
            print("\nPrioridades:", flush=True)
            for v in self.ordem_aprendida:
                print(f"  {v}: {env.prioridades[v]}", flush=True)

            if hasattr(env, 'nomes_originais') and env.nomes_originais:
                print("\nMapeamento para nomes originais:", flush=True)
                for v in self.ordem_aprendida:
                    nome_orig = env.nomes_originais.get(v, v)
                    print(f"  {v} = {nome_orig}", flush=True)

            print("\n" + "="*50, flush=True)
            print("APRENDIZADO CONCLUIDO COM SUCESSO!", flush=True)
            print("="*50 + "\n", flush=True)

            sys.stdout.flush()

            # ========================================
            # FASE DE SIMULACAO
            # ========================================
            num_sim = self.num_simulacoes

            print("="*60, flush=True)
            print("FASE DE SIMULACAO", flush=True)
            print(f"Executando {num_sim} episodios com politica aprendida vs aleatoria", flush=True)
            print("="*60, flush=True)

            # 1) Episodios com politica aprendida (greedy)
            recompensas_aprendida = []
            acertos_aprendida = []

            for ep_sim in range(num_sim):
                estado = env.possible_starts.copy()
                recompensa_ep = 0
                acertos_ep = 0
                total_ep = 0

                while True:
                    estado_tupla = self.estado_para_tupla(estado)
                    veiculos_disponiveis = [
                        v for v in env.veiculos_ids
                        if estado[env.veiculo_map[v]] == 0
                    ]
                    if not veiculos_disponiveis:
                        break

                    q_values = {v: self.q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
                    veiculo_escolhido = max(q_values, key=q_values.get)

                    novo_estado, recompensa, terminado = env.transicao_escolher(estado, veiculo_escolhido)
                    recompensa_ep += recompensa
                    total_ep += 1

                    melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
                    if env.prioridades[veiculo_escolhido] == melhor_prioridade:
                        acertos_ep += 1

                    estado = novo_estado
                    if terminado:
                        break

                recompensas_aprendida.append(recompensa_ep)
                acertos_aprendida.append(acertos_ep / total_ep * 100 if total_ep > 0 else 0)

            # 2) Episodios com politica aleatoria (baseline)
            recompensas_aleatoria = []
            acertos_aleatoria = []

            for ep_sim in range(num_sim):
                estado = env.possible_starts.copy()
                recompensa_ep = 0
                acertos_ep = 0
                total_ep = 0

                while True:
                    veiculos_disponiveis = [
                        v for v in env.veiculos_ids
                        if estado[env.veiculo_map[v]] == 0
                    ]
                    if not veiculos_disponiveis:
                        break

                    veiculo_escolhido = random.choice(veiculos_disponiveis)

                    novo_estado, recompensa, terminado = env.transicao_escolher(estado, veiculo_escolhido)
                    recompensa_ep += recompensa
                    total_ep += 1

                    melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
                    if env.prioridades[veiculo_escolhido] == melhor_prioridade:
                        acertos_ep += 1

                    estado = novo_estado
                    if terminado:
                        break

                recompensas_aleatoria.append(recompensa_ep)
                acertos_aleatoria.append(acertos_ep / total_ep * 100 if total_ep > 0 else 0)

            # 3) Step-by-step detalhado
            print("\n" + "-"*60, flush=True)
            print("STEP-BY-STEP: 1 Episodio com Politica Aprendida", flush=True)
            print("-"*60, flush=True)

            estado = env.possible_starts.copy()
            passo = 1

            while True:
                estado_tupla = self.estado_para_tupla(estado)
                veiculos_disponiveis = [
                    v for v in env.veiculos_ids
                    if estado[env.veiculo_map[v]] == 0
                ]
                if not veiculos_disponiveis:
                    break

                q_values = {v: self.q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
                veiculo_escolhido = max(q_values, key=q_values.get)

                melhor_prioridade = max(env.prioridades[v] for v in veiculos_disponiveis)
                escolha_correta = (env.prioridades[veiculo_escolhido] == melhor_prioridade)

                nome_orig = env.nomes_originais.get(veiculo_escolhido, veiculo_escolhido)
                prioridade = env.prioridades[veiculo_escolhido]
                status_str = "CORRETO" if escolha_correta else "INCORRETO"

                print(f"  Passo {passo}: {nome_orig} (prio={prioridade}) [{status_str}]", flush=True)

                novo_estado, _, terminado = env.transicao_escolher(estado, veiculo_escolhido)
                estado = novo_estado
                passo += 1

                if terminado:
                    break

            # 4) Tabela comparativa
            import statistics

            media_rec_aprendida = statistics.mean(recompensas_aprendida)
            media_rec_aleatoria = statistics.mean(recompensas_aleatoria)
            media_acerto_aprendida = statistics.mean(acertos_aprendida)
            media_acerto_aleatoria = statistics.mean(acertos_aleatoria)
            std_rec_aprendida = statistics.stdev(recompensas_aprendida) if len(recompensas_aprendida) > 1 else 0
            std_rec_aleatoria = statistics.stdev(recompensas_aleatoria) if len(recompensas_aleatoria) > 1 else 0

            print("\n" + "-"*60, flush=True)
            print("COMPARACAO: Politica Aprendida vs Aleatoria", flush=True)
            print("-"*60, flush=True)
            print(f"{'Metrica':<25} {'Aprendida':>12} {'Aleatoria':>12}", flush=True)
            print(f"{'-'*25} {'-'*12} {'-'*12}", flush=True)
            print(f"{'Recompensa media':<25} {media_rec_aprendida:>12.2f} {media_rec_aleatoria:>12.2f}", flush=True)
            print(f"{'Desvio padrao':<25} {std_rec_aprendida:>12.2f} {std_rec_aleatoria:>12.2f}", flush=True)
            print(f"{'Taxa de acerto (%)':<25} {media_acerto_aprendida:>12.2f} {media_acerto_aleatoria:>12.2f}", flush=True)
            print(f"\nMelhoria: {media_rec_aprendida - media_rec_aleatoria:+.2f} recompensa, "
                  f"{media_acerto_aprendida - media_acerto_aleatoria:+.2f}pp acerto", flush=True)
            print("="*60 + "\n", flush=True)

            # 5) Registrar metricas de simulacao
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_recompensa_media"] = media_rec_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_taxa_acerto"] = media_acerto_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_std"] = std_rec_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_recompensa_media"] = media_rec_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_taxa_acerto"] = media_acerto_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_std"] = std_rec_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_num_episodios"] = num_sim

            sys.stdout.flush()

            # ========================================
            # FASE 2: COORDENACAO MULTI-AGENTE
            # ========================================
            self._update_status("coordenando")
            self.add(Goal("coordenar_travessia"))

        except Exception as e:
            self.error_print(f"ERRO durante aprendizado: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            self.stop_cycle()

    @pl(gain, Goal("coordenar_travessia"))
    def coordenar_travessia(self, src):
        """
        Fase 2: Coordenacao multi-agente usando politica aprendida.
        Descobre veiculos ativos, solicita propostas, decide ordem.
        """
        self.info_print("\n" + "="*60)
        self.info_print("FASE DE COORDENACAO MULTI-AGENTE")
        self.info_print("="*60)

        # Descobrir veiculos ativos via MASPY
        veiculos_encontrados = self.list_agents("VeiculoLearningAgent")

        if not veiculos_encontrados:
            self.info_print("Nenhum VeiculoLearningAgent encontrado. Encerrando.")
            self._update_status("concluido")
            self.stop_cycle()
            return

        self.num_veiculos_esperados = len(veiculos_encontrados)
        self.propostas_recebidas = []

        self.info_print(f"Veiculos encontrados ({len(veiculos_encontrados)}): {veiculos_encontrados}")
        self.info_print("Solicitando propostas de todos os veiculos...")

        # Enviar solicitacao de proposta para cada veiculo via canal "comunicacao"
        for veiculo_name in veiculos_encontrados:
            self.send(veiculo_name, tell, Belief("solicitar_proposta", self.my_name), "comunicacao")
            self.comm_stats["mensagens_enviadas"] += 1
            self.comm_stats["solicitacoes_enviadas"] += 1

        self.info_print("Aguardando propostas dos veiculos...")

    @pl(gain, Belief("proposta", Any))
    def receber_proposta(self, src, dados):
        """
        Recebe proposta de um veiculo.
        Quando todas as propostas chegam, decide a ordem.
        """
        self.propostas_recebidas.append(dados)
        self.comm_stats["mensagens_recebidas"] += 1
        self.comm_stats["propostas_recebidas"] += 1
        self.debug_print(f"Proposta recebida de {src}: {dados}")

        if len(self.propostas_recebidas) >= self.num_veiculos_esperados:
            self.info_print(f"\nTodas as {len(self.propostas_recebidas)} propostas recebidas!")
            self.add(Goal("decidir_ordem"))

    @pl(gain, Goal("decidir_ordem"))
    def decidir_ordem(self, src):
        """
        Decide a ordem de travessia usando a Q-table aprendida.
        Comunica decisoes a cada veiculo.
        """
        env = self.env
        self.info_print("\n" + "-"*60)
        self.info_print("DECIDINDO ORDEM COM POLITICA APRENDIDA")
        self.info_print("-"*60)

        # Usar Q-table para decidir a ordem
        ordem_final = []
        estado_temp = env.possible_starts.copy()

        while len(ordem_final) < len(env.veiculos_ids):
            estado_tupla = self.estado_para_tupla(estado_temp)
            disponiveis = [v for v in env.veiculos_ids
                         if estado_temp[env.veiculo_map[v]] == 0]

            if not disponiveis:
                break

            q_values = {v: self.q_table[(estado_tupla, v)] for v in disponiveis}
            melhor_veiculo = max(q_values, key=q_values.get)

            ordem_final.append(melhor_veiculo)
            estado_temp[env.veiculo_map[melhor_veiculo]] = 1

        self.info_print(f"Ordem decidida: {' -> '.join(ordem_final)}")

        # Mapear VeiculoX -> nome do agente MASPY correspondente
        veiculos_encontrados = self.list_agents("VeiculoLearningAgent") or []

        # Construir mapeamento veiculo_id -> agent_name
        veiculo_id_to_agent = {}
        for prop in self.propostas_recebidas:
            veiculo_id_to_agent[prop["veiculo_id"]] = prop["agent_name"]

        # Enviar decisao para cada veiculo com sua posicao na ordem
        for posicao, veiculo_id in enumerate(ordem_final):
            agent_name = veiculo_id_to_agent.get(veiculo_id)
            if agent_name:
                decisao = {
                    "posicao": posicao + 1,
                    "veiculo_id": veiculo_id,
                    "total": len(ordem_final),
                    "prioridade": env.prioridades.get(veiculo_id, 0)
                }
                nome_orig = env.nomes_originais.get(veiculo_id, veiculo_id)
                self.info_print(f"  Posicao {posicao + 1}: {nome_orig} (prio={decisao['prioridade']}) -> {agent_name}")
                self.send(agent_name, tell, Belief("decisao", decisao), "comunicacao")
                self.comm_stats["mensagens_enviadas"] += 1
                self.comm_stats["decisoes_enviadas"] += 1

        # Enviar ordem completa para todos os veiculos
        ordem_info = {
            "ordem": ordem_final,
            "prioridades": {v: env.prioridades[v] for v in ordem_final},
            "nomes_originais": {v: env.nomes_originais.get(v, v) for v in ordem_final}
        }
        for agent_name in veiculos_encontrados:
            self.send(agent_name, tell, Belief("ordem_completa", ordem_info), "comunicacao")
            self.comm_stats["mensagens_enviadas"] += 1
            self.comm_stats["ordens_enviadas"] += 1

        self.info_print("\n" + "="*60)
        self.info_print("COORDENACAO MULTI-AGENTE CONCLUIDA!")
        self.info_print("="*60 + "\n")

        self._update_status("concluido")
        self.stop_cycle()



# AGENTE DE VEICULO COM COMUNICACAO MULTI-AGENTE

class VeiculoLearningAgent(LoggableAgent):
    """
    Agente que representa um veiculo individual no cruzamento.
    Participa ativamente da coordenacao multi-agente:
    - Recebe solicitacao de proposta do coordenador
    - Envia proposta com suas informacoes (id, prioridade, tipo)
    - Recebe decisao do coordenador com sua posicao na ordem
    - Recebe ordem completa e encerra
    """

    def __init__(self, agt_name=None, veiculo_id=None, prioridade=10, tipo="carro", log_level=None):
        super().__init__(agt_name, log_level)

        self.veiculo_id = veiculo_id
        self.prioridade = prioridade
        self.tipo = tipo

        # Beliefs observaveis
        self.add(Belief("veiculo_id", veiculo_id))
        self.add(Belief("prioridade", prioridade))
        self.add(Belief("tipo", tipo))
        self.add(Belief("status", "aguardando"))

        # Metricas
        self.posicao_recebida = None
        self.historico_acoes = []
        self.recompensa_acumulada = 0

        # Contadores de comunicacao
        self.comm_stats = {
            "mensagens_enviadas": 0,
            "mensagens_recebidas": 0,
        }

        # Registrar no coletor de metricas
        METRICS_COLLECTOR.registrar_agente(agt_name)

    def _update_belief(self, belief_name, value):
        """Atualiza um belief observavel."""
        old_belief = self.get(Belief(belief_name, Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief(belief_name, value))

    @pl(gain, Belief("solicitar_proposta", Any))
    def enviar_proposta(self, src, coordenador_name):
        """
        Recebe solicitacao do coordenador e envia proposta.
        Usa send() via canal "comunicacao" para comunicacao inter-agente.
        """
        self._update_belief("status", "propondo")
        self.debug_print(f"[{self.my_name}] Recebida solicitacao de {src}. Enviando proposta...")

        # Descobrir coordenador via MASPY
        coordenadores = self.list_agents("CoordenadorLearningAgent")
        if not coordenadores:
            self.error_print(f"[{self.my_name}] Nenhum coordenador encontrado!")
            return

        coord_name = coordenadores[0]

        proposta = {
            "agent_name": self.my_name,
            "veiculo_id": self.veiculo_id,
            "prioridade": self.prioridade,
            "tipo": self.tipo,
        }

        self.send(coord_name, tell, Belief("proposta", proposta), "comunicacao")
        self.comm_stats["mensagens_enviadas"] += 1
        self.debug_print(f"[{self.my_name}] Proposta enviada: veiculo_id={self.veiculo_id}, prio={self.prioridade}")

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, decisao):
        """
        Recebe decisao do coordenador com a posicao na ordem de travessia.
        """
        self.posicao_recebida = decisao.get("posicao", 0)
        total = decisao.get("total", 0)
        self.comm_stats["mensagens_recebidas"] += 1

        self._update_belief("status", "atravessando")

        self.info_print(
            f"[{self.my_name}] Decisao recebida: posicao {self.posicao_recebida}/{total} "
            f"(veiculo_id={self.veiculo_id}, prio={self.prioridade})"
        )

    @pl(gain, Belief("ordem_completa", Any))
    def receber_ordem_completa(self, src, ordem_info):
        """
        Recebe a ordem completa de travessia e encerra o ciclo.
        """
        ordem = ordem_info.get("ordem", [])
        self.comm_stats["mensagens_recebidas"] += 1
        self._update_belief("status", "concluido")

        self.debug_print(f"[{self.my_name}] Ordem completa recebida: {' -> '.join(ordem)}")
        self.stop_cycle()

    def obter_estatisticas(self):
        """Retorna estatisticas do veiculo."""
        return {
            "veiculo_id": self.veiculo_id,
            "prioridade": self.prioridade,
            "tipo": self.tipo,
            "posicao_recebida": self.posicao_recebida,
            "recompensa_acumulada": self.recompensa_acumulada,
            "total_acoes": len(self.historico_acoes)
        }
