"""
Ambiente de Aprendizado para Cruzamento
Implementa Q-Learning para ordenacao de veiculos por prioridade.
Fornece Percepts para coordenacao multi-agente.
"""

from maspy import *
from maspy.learning import *
from .config import VEICULOS_CONFIG
from .utils import Cores, cor


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
        veiculos_config_original = config_base  # Máximo 10 veículos


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

        # Percepts para coordenacao multi-agente
        self.create(Percept("cruzamento_status", ("livre", "ocupado", "coordenando"), listed))
        self.create(Percept("rodada_atual", 0))

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

    @action(listed, tuple(f"Veiculo{i}" for i in range(1, 16)), transicao_escolher)
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

    def atualizar_status_cruzamento(self, novo_status):
        """Atualiza o Percept de status do cruzamento para notificar agentes."""
        self.change(Percept("cruzamento_status", Any), novo_status)

    def avancar_rodada(self):
        """Avanca a rodada atual e notifica agentes via Percept."""
        rodada_atual = self.get(Percept("rodada_atual", Any))
        nova_rodada = (rodada_atual.args if rodada_atual else 0) + 1
        self.change(Percept("rodada_atual", Any), nova_rodada)
        return nova_rodada
