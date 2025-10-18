# cruzamento_maspy.py
# Sistema Multi-Agentes para Negociação em Cruzamento usando MASPY
# Implementação com framework MASPY seguindo arquitetura BDI

from maspy import *
from random import randint, choice

# ============================================================================
# AMBIENTE - CRUZAMENTO
# ============================================================================

class CruzamentoEnvironment(Environment):
    """
    Ambiente que representa um cruzamento de 4 vias
    Gerencia o estado compartilhado e percepções dos agentes
    """

    def __init__(self):
        super().__init__()
        self.ocupado = False
        self.veiculo_atual = None
        self.tempo_atual = 0.0
        self.estatisticas = {
            'ordem_passagem': [],
            'tempos_espera': {}
        }

    # Action: Veículo anuncia intenção de atravessar
    def anunciar_intencao(self, agt, proposta):
        """
        Veículo anuncia que deseja atravessar
        proposta = {'veiculo_id': id, 'direcao': dir, 'tipo': tipo, 'prioridade': valor, 'tempo_espera': tempo}
        """
        self.print(f"[ANUNCIO] {agt} da direcao {proposta['direcao']} - Tipo: {proposta['tipo']}, Prioridade: {proposta['prioridade']:.2f}")

        # Cria percepção visível para o coordenador
        self.create(Percept("proposta", {
            "veiculo": str(agt),
            "direcao": proposta['direcao'],
            "tipo": proposta['tipo'],
            "prioridade": proposta['prioridade'],
            "tempo_espera": proposta['tempo_espera']
        }))

    # Action: Ocupar o cruzamento
    def ocupar_cruzamento(self, agt):
        """Veículo ocupa o cruzamento"""
        if not self.ocupado:
            self.ocupado = True
            self.veiculo_atual = str(agt)
            self.print(f">>> {agt} OCUPOU o cruzamento")

            # Cria percepção de cruzamento ocupado
            self.create(Percept("cruzamento_ocupado", {"veiculo": str(agt)}))
            return True
        return False

    # Action: Liberar o cruzamento
    def liberar_cruzamento(self, agt, tempo_espera):
        """Veículo libera o cruzamento após atravessar"""
        if self.ocupado and self.veiculo_atual == str(agt):
            self.ocupado = False
            self.veiculo_atual = None
            self.print(f">>> {agt} LIBEROU o cruzamento (esperou {tempo_espera:.1f}s)")

            # Remove percepção de ocupado
            self.delete(Percept("cruzamento_ocupado", {"veiculo": str(agt)}))

            # Registra estatísticas
            self.estatisticas['ordem_passagem'].append(str(agt))
            self.estatisticas['tempos_espera'][str(agt)] = tempo_espera

            return True
        return False

    # Action: Remover proposta após processamento
    def remover_proposta(self, agt, proposta):
        """Remove proposta do ambiente após processamento"""
        self.delete(Percept("proposta", proposta))

    def exibir_estatisticas(self):
        """Exibe estatísticas finais"""
        self.print("\n" + "="*60)
        self.print("ESTATISTICAS FINAIS")
        self.print("="*60)

        if self.estatisticas['ordem_passagem']:
            self.print(f"\nOrdem de passagem ({len(self.estatisticas['ordem_passagem'])} veiculos):")
            for i, veiculo in enumerate(self.estatisticas['ordem_passagem'], 1):
                tempo = self.estatisticas['tempos_espera'].get(veiculo, 0)
                self.print(f"  {i}. {veiculo} - Tempo de espera: {tempo:.1f}s")

            tempos = list(self.estatisticas['tempos_espera'].values())
            self.print(f"\nTempo medio de espera: {sum(tempos)/len(tempos):.2f}s")
            self.print(f"Tempo minimo: {min(tempos):.2f}s")
            self.print(f"Tempo maximo: {max(tempos):.2f}s")

        self.print("="*60)

# ============================================================================
# AGENTE - VEÍCULO
# ============================================================================

class VeiculoAgent(Agent):
    """
    Agente que representa um veículo autônomo
    Usa arquitetura BDI para decidir quando e como atravessar
    """

    def __init__(self, agt_name, direcao, tipo='normal', tempo_travessia=3.0):
        super().__init__(agt_name)

        # Beliefs iniciais
        self.add(Belief("direcao", direcao))
        self.add(Belief("tipo", tipo))
        self.add(Belief("tempo_travessia", tempo_travessia))
        self.add(Belief("tempo_chegada", 0.0))
        self.add(Belief("estado", "aguardando"))  # aguardando, negociando, atravessando, concluido

        # Goal inicial: atravessar o cruzamento
        self.add(Goal("atravessar"))

    # ========================================================================
    # PLANO 1: Iniciar processo de negociação
    # Gatilho: Ganhar objetivo "atravessar"
    # Contexto: Estado é "aguardando"
    # ========================================================================
    @pl(gain, Goal("atravessar"), Belief("estado", "aguardando"))
    def iniciar_negociacao(self, src):
        """Inicia o processo de negociação para atravessar"""
        self.wait(0.5)  # Pequena espera antes de anunciar

        # Busca beliefs necessários
        direcao = self.get(Belief("direcao")).args
        tipo = self.get(Belief("tipo")).args
        tempo_chegada = self.get(Belief("tempo_chegada")).args

        # Calcula tempo de espera e prioridade
        tempo_espera = 0.5  # Simulação simples
        prioridade = self.calcular_prioridade(tempo_espera, tipo)

        # Monta proposta
        proposta = {
            'veiculo_id': self.str_name,
            'direcao': direcao,
            'tipo': tipo,
            'prioridade': prioridade,
            'tempo_espera': tempo_espera
        }

        self.print(f"Enviando proposta: prioridade={prioridade:.2f}, tipo={tipo}")

        # Atualiza estado
        self.remove(Belief("estado", "aguardando"))
        self.add(Belief("estado", "negociando"))

        # Anuncia intenção no ambiente
        self.anunciar_intencao(proposta)

        # Envia proposta ao coordenador
        self.send("Coordenador", achieve, Goal("avaliar_proposta", proposta))

    # ========================================================================
    # PLANO 2: Receber permissão para atravessar
    # Gatilho: Ganhar belief "permissao"
    # Contexto: Estado é "negociando"
    # ========================================================================
    @pl(gain, Belief("permissao"), Belief("estado", "negociando"))
    def executar_travessia(self, src):
        """Executa a travessia após receber permissão"""
        tipo = self.get(Belief("tipo")).args
        tipo_str = "EMERGENCIA" if tipo == 'emergencia' else "Normal"

        self.print(f"[{tipo_str}] Recebi PERMISSAO! Iniciando travessia...")

        # Atualiza estado
        self.remove(Belief("estado", "negociando"))
        self.add(Belief("estado", "atravessando"))

        # Ocupa o cruzamento
        sucesso = self.ocupar_cruzamento()

        if sucesso:
            # Simula tempo de travessia
            tempo_travessia = self.get(Belief("tempo_travessia")).args
            self.wait(tempo_travessia)

            # Adiciona objetivo de sair do cruzamento
            self.add(Goal("sair_cruzamento"))
        else:
            self.print(f"ERRO: Nao consegui ocupar o cruzamento!")
            self.stop_cycle()

    # ========================================================================
    # PLANO 3: Sair do cruzamento após atravessar
    # Gatilho: Ganhar objetivo "sair_cruzamento"
    # Contexto: Estado é "atravessando"
    # ========================================================================
    @pl(gain, Goal("sair_cruzamento"), Belief("estado", "atravessando"))
    def finalizar_travessia(self, src):
        """Libera o cruzamento e finaliza"""
        tempo_espera = self.get(Belief("tempo_espera", "TempoEspera"), ck_src=False)
        if tempo_espera:
            tempo_val = tempo_espera.args
        else:
            tempo_val = 0.5

        # Libera o cruzamento
        self.liberar_cruzamento(tempo_val)

        # Atualiza estado final
        self.remove(Belief("estado", "atravessando"))
        self.add(Belief("estado", "concluido"))

        self.print(f"Travessia CONCLUIDA!")

        # Para o ciclo de raciocínio
        self.stop_cycle()

    # ========================================================================
    # PLANO 4: Receber negação (outro veículo foi escolhido)
    # Gatilho: Ganhar belief "negado"
    # Contexto: Estado é "negociando"
    # ========================================================================
    @pl(gain, Belief("negado"), Belief("estado", "negociando"))
    def proposta_negada(self, src):
        """Volta a aguardar quando proposta é negada"""
        self.print(f"Proposta NEGADA. Aguardando proxima rodada...")

        # Volta ao estado de aguardo
        self.remove(Belief("estado", "negociando"))
        self.add(Belief("estado", "aguardando"))

        # Incrementa tempo de espera
        tempo_atual = self.get(Belief("tempo_espera", "TempoEspera"), ck_src=False)
        if tempo_atual:
            novo_tempo = tempo_atual.args + 1.0
            self.remove(Belief("tempo_espera", tempo_atual.args))
        else:
            novo_tempo = 1.0

        self.add(Belief("tempo_espera", novo_tempo))

        # Tenta novamente
        self.wait(1.0)
        self.add(Goal("atravessar"))

    # ========================================================================
    # Funções auxiliares (não são planos)
    # ========================================================================

    def calcular_prioridade(self, tempo_espera, tipo):
        """Calcula prioridade baseada em tempo de espera e tipo"""
        prioridade_tempo = tempo_espera * 0.1
        bonus_emergencia = 100.0 if tipo == 'emergencia' else 0.0
        fator_aleatorio = randint(0, 50) / 100.0  # 0 a 0.5

        return prioridade_tempo + bonus_emergencia + fator_aleatorio

# ============================================================================
# AGENTE - COORDENADOR
# ============================================================================

class CoordenadorAgent(Agent):
    """
    Agente coordenador que gerencia o protocolo de negociação
    Recebe propostas e decide qual veículo pode atravessar
    """

    def __init__(self):
        super().__init__("Coordenador")

        # Beliefs iniciais
        self.add(Belief("rodada", 0))
        self.add(Belief("total_decisoes", 0))

    # ========================================================================
    # PLANO: Avaliar proposta recebida
    # Gatilho: Ganhar objetivo "avaliar_proposta(Proposta)"
    # Contexto: Nenhum
    # ========================================================================
    @pl(gain, Goal("avaliar_proposta", "Proposta"))
    def processar_proposta(self, src, proposta):
        """
        Recebe uma proposta e inicia processo de avaliação
        Aguarda um pouco para coletar mais propostas
        """
        self.print(f"Proposta recebida de {proposta['veiculo_id']}")

        # Aguarda para coletar outras propostas
        self.wait(0.3)

        # Adiciona objetivo de decidir
        self.add(Goal("decidir_vencedor"))

    # ========================================================================
    # PLANO: Decidir qual veículo pode atravessar
    # Gatilho: Ganhar objetivo "decidir_vencedor"
    # Contexto: Nenhum
    # ========================================================================
    @pl(gain, Goal("decidir_vencedor"))
    def decidir_vencedor(self, src):
        """
        Avalia todas as propostas disponíveis e escolhe o vencedor
        """
        # Busca todas as propostas percebidas no ambiente
        propostas = self.get(Belief("proposta", "Caracteristicas"), all=True, ck_src=False)

        if propostas is None or len(propostas) == 0:
            self.print("Nenhuma proposta disponivel para avaliar")
            return

        self.print(f"\n{'─'*60}")
        self.print(f"COORDENADOR: Avaliando {len(propostas)} proposta(s)")
        self.print(f"{'─'*60}")

        # Separa emergências de normais
        emergencias = []
        normais = []

        for prop in propostas:
            assert isinstance(prop, Belief)
            dados = prop.args

            self.print(f"  - {dados['veiculo']}: tipo={dados['tipo']}, prioridade={dados['prioridade']:.2f}")

            if dados['tipo'] == 'emergencia':
                emergencias.append(dados)
            else:
                normais.append(dados)

        # Escolhe vencedor (prioriza emergências)
        if emergencias:
            # Entre emergências, escolhe por maior prioridade
            vencedor = max(emergencias, key=lambda p: p['prioridade'])
            self.print(f"\n>>> EMERGENCIA detectada! Prioridade maxima.")
        else:
            # Entre normais, escolhe por maior prioridade
            vencedor = max(normais, key=lambda p: p['prioridade'])
            self.print(f"\n>>> Criterio: Maior prioridade (tempo + tipo)")

        self.print(f">>> VENCEDOR: {vencedor['veiculo']}")

        # Concede permissão ao vencedor
        self.send(vencedor['veiculo'], tell, Belief("permissao"))

        # Nega os demais
        for prop in propostas:
            dados = prop.args
            if dados['veiculo'] != vencedor['veiculo']:
                self.send(dados['veiculo'], tell, Belief("negado"))
                self.print(f">>> NEGADO: {dados['veiculo']}")

        # Remove todas as propostas do ambiente
        for prop in propostas:
            self.remover_proposta(prop.args)

        # Atualiza estatísticas
        total = self.get(Belief("total_decisoes")).args
        self.remove(Belief("total_decisoes", total))
        self.add(Belief("total_decisoes", total + 1))

        self.print(f"{'─'*60}\n")

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SISTEMA MULTI-AGENTES - CRUZAMENTO (MASPY)")
    print("="*60)

    # Cria o ambiente
    cruzamento = CruzamentoEnvironment()

    # Cria o coordenador
    coordenador = CoordenadorAgent()

    # Cria veículos
    direcoes = ['norte', 'sul', 'leste', 'oeste']
    veiculos = []

    # Primeiro veículo é emergência
    v1 = VeiculoAgent("V1_Ambulancia", choice(direcoes), tipo='emergencia', tempo_travessia=2.0)
    veiculos.append(v1)

    # Demais veículos são normais
    for i in range(2, 6):
        direcao = choice(direcoes)
        veiculo = VeiculoAgent(f"V{i}", direcao, tipo='normal', tempo_travessia=3.0)
        veiculos.append(veiculo)

    print(f"\nConfiguracao:")
    print(f"  • Total de veiculos: {len(veiculos)}")
    for v in veiculos:
        tipo_belief = v.get(Belief("tipo", "Tipo"), ck_src=False)
        direcao_belief = v.get(Belief("direcao", "Direcao"), ck_src=False)

        if tipo_belief and direcao_belief:
            tipo_str = "EMERGENCIA" if tipo_belief.args == 'emergencia' else "Normal"
            print(f"  [{tipo_str}] {v.str_name} - Direcao: {direcao_belief.args}")
        else:
            print(f"  {v.str_name} - (Configuracao pendente)")

    print("\nIniciando simulacao...")
    print("="*60 + "\n")

    # Conecta todos os agentes ao ambiente
    agent_list = veiculos + [coordenador]
    Admin().connect_to(agent_list, cruzamento)

    # Configurações do Admin
    Admin().report = True

    # Inicia o sistema
    Admin().start_system()

    # Exibe estatísticas finais
    cruzamento.exibir_estatisticas()
