# cruzamento_maspy_simples.py
# Sistema Multi-Agentes para Negociação em Cruzamento usando MASPY
# Versão Simplificada e Funcional

from maspy import *
from random import randint, choice

# ============================================================================
# AMBIENTE - CRUZAMENTO
# ============================================================================

class CruzamentoEnvironment(Environment):
    """Ambiente que representa um cruzamento"""

    def __init__(self):
        super().__init__()
        # Cria percepção inicial
        self.create(Percept("iniciar_negociacao"))

    def registrar_passagem(self, agt, tempo_espera):
        """Registra a passagem de um veículo"""
        self.print(f">>> {agt} atravessou o cruzamento (esperou {tempo_espera:.1f}s)")

# ============================================================================
# AGENTE - VEÍCULO
# ============================================================================

class VeiculoAgent(Agent):
    """Agente que representa um veículo autônomo"""

    def __init__(self, agt_name, direcao, tipo='normal'):
        super().__init__(agt_name)

        # Beliefs iniciais
        self.add(Belief("direcao", direcao))
        self.add(Belief("tipo", tipo))
        self.add(Belief("tempo_espera", randint(1, 5) * 1.0))

        # Goal inicial
        self.add(Goal("enviar_proposta"))

    # Plano: Enviar proposta ao coordenador
    @pl(gain, Goal("enviar_proposta"))
    def enviar_proposta(self, src):
        """Envia proposta ao coordenador"""
        tipo = self.get(Belief("tipo")).args
        tempo_espera = self.get(Belief("tempo_espera")).args

        # Calcula prioridade
        if tipo == 'emergencia':
            prioridade = 100.0 + randint(0, 10)
        else:
            prioridade = tempo_espera * 0.5 + randint(0, 5)

        self.print(f"Proposta: tipo={tipo}, prioridade={prioridade:.2f}, espera={tempo_espera:.1f}s")

        # Envia ao coordenador
        proposta = {
            'veiculo': self.my_name,
            'tipo': tipo,
            'prioridade': prioridade,
            'tempo_espera': tempo_espera
        }

        self.send("Coordenador", tell, Belief("proposta", proposta))

    # Plano: Receber permissão
    @pl(gain, Belief("permissao"))
    def atravessar(self, src):
        """Atravessa o cruzamento"""
        tipo = self.get(Belief("tipo")).args
        tempo_espera = self.get(Belief("tempo_espera")).args
        tipo_str = "EMERGENCIA" if tipo == 'emergencia' else "Normal"

        self.print(f"[{tipo_str}] PERMISSAO recebida! Atravessando...")

        # Registra no ambiente
        self.registrar_passagem(tempo_espera)

        self.print(f"[{tipo_str}] Travessia CONCLUIDA!")
        self.stop_cycle()

    # Plano: Proposta negada
    @pl(gain, Belief("negado"))
    def aguardar(self, src):
        """Aguarda quando negado"""
        self.print("Proposta NEGADA.")
        self.stop_cycle()

# ============================================================================
# AGENTE - COORDENADOR
# ============================================================================

class CoordenadorAgent(Agent):
    """Agente coordenador"""

    def __init__(self):
        super().__init__("Coordenador")
        self.propostas_recebidas = []
        self.add(Goal("aguardar_propostas"))

    # Plano: Receber proposta
    @pl(gain, Belief("proposta", "Dados"))
    def receber_proposta(self, src, dados):
        """Recebe proposta de um veículo"""
        self.print(f"Proposta de {dados['veiculo']}: prioridade={dados['prioridade']:.2f}")
        self.propostas_recebidas.append(dados)

    # Plano: Aguardar e decidir
    @pl(gain, Goal("aguardar_propostas"))
    def aguardar_e_decidir(self, src):
        """Aguarda propostas e decide"""
        self.print("\n" + "-"*60)
        self.print("COORDENADOR: Aguardando propostas...")
        self.print("-"*60)

        # Aguarda para coletar propostas
        self.wait(2.0)

        if len(self.propostas_recebidas) == 0:
            self.print("Nenhuma proposta recebida")
            self.stop_cycle()
            return

        self.print(f"\nAv aliando {len(self.propostas_recebidas)} proposta(s)...")

        # Separa emergências
        emergencias = [p for p in self.propostas_recebidas if p['tipo'] == 'emergencia']
        normais = [p for p in self.propostas_recebidas if p['tipo'] == 'normal']

        # Escolhe vencedor
        if emergencias:
            vencedor = max(emergencias, key=lambda p: p['prioridade'])
            self.print(">>> EMERGENCIA detectada! Prioridade maxima.")
        else:
            vencedor = max(normais, key=lambda p: p['prioridade'])
            self.print(">>> Criterio: Maior prioridade")

        self.print(f">>> VENCEDOR: {vencedor['veiculo']}")

        # Concede permissão
        self.send(vencedor['veiculo'], tell, Belief("permissao"))

        # Nega os demais
        for prop in self.propostas_recebidas:
            if prop['veiculo'] != vencedor['veiculo']:
                self.send(prop['veiculo'], tell, Belief("negado"))
                self.print(f">>> NEGADO: {prop['veiculo']}")

        self.print("-"*60 + "\n")
        self.stop_cycle()

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
    v1 = VeiculoAgent("V1_Ambulancia", choice(direcoes), tipo='emergencia')
    veiculos.append(v1)

    # Demais veículos são normais
    for i in range(2, 6):
        direcao = choice(direcoes)
        veiculo = VeiculoAgent(f"V{i}", direcao, tipo='normal')
        veiculos.append(veiculo)

    print(f"\nConfiguracao:")
    print(f"  • Total de veiculos: {len(veiculos)}")
    print(f"  [EMERGENCIA] V1_Ambulancia")
    for i in range(2, 6):
        print(f"  [Normal] V{i}")

    print("\nIniciando simulacao...")
    print("="*60 + "\n")

    # Conecta todos os agentes ao ambiente
    agent_list = veiculos + [coordenador]
    Admin().connect_to(agent_list, cruzamento)

    # Inicia o sistema
    Admin().start_system()

    print("\n" + "="*60)
    print("SIMULACAO CONCLUIDA")
    print("="*60)
