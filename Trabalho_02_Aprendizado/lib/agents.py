"""
Agentes para Sistema de Aprendizado
Contém agentes que implementam Q-Learning para ordenação de veículos.

Extraído de: cruzamento_maspy_learning.py (linhas 329-1669)
"""

import sys
import random
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



# AGENTE DE APRENDIZADO

class CoordenadorLearningAgent(LoggableAgent):
    """
    Agente coordenador que usa Q-Learning para aprender
    a ordem ótima de travessia dos veículos.
    """

    def __init__(self, agt_name=None, env=None, num_episodes=100, num_simulacoes=20, log_level=None):
        super().__init__(agt_name, log_level)

        self.env = env
        self.num_episodes = num_episodes
        self.num_simulacoes = num_simulacoes
        self.q_table = defaultdict(float)

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

    def estado_para_tupla(self, estado_dict):
        """Converte estado dict para tupla ordenada (hashable)."""
        env = self.env
        return tuple(estado_dict[env.veiculo_map[v]] for v in env.veiculos_ids)

    def escolher_acao_epsilon_greedy(self, estado_tupla, veiculos_disponiveis, epsilon):
        """Escolhe ação usando estratégia epsilon-greedy."""
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
            self.info_print("\nExecutando treinamento com coleta de métricas...")

            # Parâmetros Q-Learning
            alpha = 0.1  # Taxa de aprendizado
            gamma = 0.9  # Fator de desconto
            epsilon = 1.0  # Exploração inicial
            epsilon_decay = 0.995
            epsilon_min = 0.01

            # Resetar Q-table persistente
            self.q_table = defaultdict(float)
            q_table = self.q_table

            # Treinar por num_episodes episódios
            for ep in range(self.num_episodes):
                estado = env.possible_starts.copy()
                estado_tupla = self.estado_para_tupla(estado)
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
                    veiculo_escolhido = self.escolher_acao_epsilon_greedy(
                        estado_tupla, veiculos_disponiveis, epsilon
                    )

                    # Executar transição e obter recompensa
                    novo_estado, recompensa, terminado = env.transicao_escolher(
                        estado, veiculo_escolhido
                    )
                    novo_estado_tupla = self.estado_para_tupla(novo_estado)

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

            # ========================================
            # FASE DE VALIDAÇÃO: Usar Q-table aprendida
            # ========================================
            self.info_print("-"*60)
            self.info_print("INICIANDO VALIDAÇÃO COM POLÍTICA APRENDIDA...")

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

                    # USAR POLÍTICA APRENDIDA (epsilon=0 - pura exploração)
                    q_values = {v: q_table[(estado_tupla, v)] for v in veiculos_disponiveis}
                    veiculo_escolhido = max(q_values, key=q_values.get)

                    # Executar ação e verificar
                    novo_estado, recompensa, terminado = env.transicao_escolher(estado, veiculo_escolhido)
                    recompensa_total_validacao += recompensa
                    total_acoes_validacao += 1

                    # Verificar se foi a escolha correta (recompensa positiva)
                    if recompensa > 0:
                        acertos_validacao += 1

                    estado = novo_estado

                    if terminado:
                        break

            # Calcular taxa de acerto da validação
            taxa_acerto_validacao = (acertos_validacao / total_acoes_validacao * 100) if total_acoes_validacao > 0 else 0
            recompensa_media_validacao = recompensa_total_validacao / num_episodios_validacao if num_episodios_validacao > 0 else 0

            self.info_print(f"Validação concluída: {num_episodios_validacao} episódios")
            self.info_print(f"Taxa de acerto (validação): {taxa_acerto_validacao:.2f}%")
            self.info_print(f"Recompensa média (validação): {recompensa_media_validacao:.2f}")

            # ========================================
            # EXTRAIR ORDEM ÓTIMA DA Q-TABLE
            # ========================================
            ordem_aprendida = []
            estado_temp = env.possible_starts.copy()

            while len(ordem_aprendida) < len(env.veiculos_ids):
                estado_tupla_temp = self.estado_para_tupla(estado_temp)
                disponiveis = [v for v in env.veiculos_ids
                             if estado_temp[env.veiculo_map[v]] == 0]

                if not disponiveis:
                    break

                # Escolher veículo com maior Q-value
                q_values_temp = {v: q_table[(estado_tupla_temp, v)] for v in disponiveis}
                melhor_veiculo = max(q_values_temp, key=q_values_temp.get)

                ordem_aprendida.append(melhor_veiculo)
                estado_temp[env.veiculo_map[melhor_veiculo]] = 1

            # Mostrar ordem ótima aprendida
            print("\n" + "="*50, flush=True)
            print("RESULTADO DO APRENDIZADO", flush=True)
            print("="*50, flush=True)

            print(f"\nOrdem ótima aprendida (via Q-table): {' -> '.join(ordem_aprendida)}", flush=True)
            print("\nPrioridades:", flush=True)
            for v in ordem_aprendida:
                print(f"  {v}: {env.prioridades[v]}", flush=True)

            # Mostrar mapeamento para nomes originais
            if hasattr(env, 'nomes_originais') and env.nomes_originais:
                print("\nMapeamento para nomes originais:", flush=True)
                for v in ordem_aprendida:
                    nome_orig = env.nomes_originais.get(v, v)
                    print(f"  {v} = {nome_orig}", flush=True)

            print("\n" + "="*50, flush=True)
            print("APRENDIZADO CONCLUÍDO COM SUCESSO!", flush=True)
            print("="*50 + "\n", flush=True)

            sys.stdout.flush()

            # ========================================
            # FASE DE SIMULAÇÃO: Aplicar política aprendida
            # ========================================
            num_sim = self.num_simulacoes

            print("="*60, flush=True)
            print("FASE DE SIMULAÇÃO", flush=True)
            print(f"Executando {num_sim} episódios com política aprendida vs aleatória", flush=True)
            print("="*60, flush=True)

            # --- 1) Episódios com política aprendida (greedy, epsilon=0) ---
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

                    # Greedy: melhor Q-value
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

            # --- 2) Episódios com política aleatória (baseline) ---
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

                    # Aleatório
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

            # --- 3) Step-by-step detalhado de 1 episódio com política aprendida ---
            print("\n" + "-"*60, flush=True)
            print("STEP-BY-STEP: 1 Episódio com Política Aprendida", flush=True)
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

            # --- 4) Tabela comparativa ---
            import statistics

            media_rec_aprendida = statistics.mean(recompensas_aprendida)
            media_rec_aleatoria = statistics.mean(recompensas_aleatoria)
            media_acerto_aprendida = statistics.mean(acertos_aprendida)
            media_acerto_aleatoria = statistics.mean(acertos_aleatoria)
            std_rec_aprendida = statistics.stdev(recompensas_aprendida) if len(recompensas_aprendida) > 1 else 0
            std_rec_aleatoria = statistics.stdev(recompensas_aleatoria) if len(recompensas_aleatoria) > 1 else 0

            print("\n" + "-"*60, flush=True)
            print("COMPARAÇÃO: Política Aprendida vs Aleatória", flush=True)
            print("-"*60, flush=True)
            print(f"{'Métrica':<25} {'Aprendida':>12} {'Aleatória':>12}", flush=True)
            print(f"{'-'*25} {'-'*12} {'-'*12}", flush=True)
            print(f"{'Recompensa média':<25} {media_rec_aprendida:>12.2f} {media_rec_aleatoria:>12.2f}", flush=True)
            print(f"{'Desvio padrão':<25} {std_rec_aprendida:>12.2f} {std_rec_aleatoria:>12.2f}", flush=True)
            print(f"{'Taxa de acerto (%)':<25} {media_acerto_aprendida:>12.2f} {media_acerto_aleatoria:>12.2f}", flush=True)
            print(f"\nMelhoria: {media_rec_aprendida - media_rec_aleatoria:+.2f} recompensa, "
                  f"{media_acerto_aprendida - media_acerto_aleatoria:+.2f}pp acerto", flush=True)
            print("="*60 + "\n", flush=True)

            # --- 5) Registrar métricas de simulação no METRICS_COLLECTOR ---
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_recompensa_media"] = media_rec_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_taxa_acerto"] = media_acerto_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aprendida_std"] = std_rec_aprendida
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_recompensa_media"] = media_rec_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_taxa_acerto"] = media_acerto_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_aleatoria_std"] = std_rec_aleatoria
            METRICS_COLLECTOR.metricas_globais["simulacao_num_episodios"] = num_sim

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
