# cruzamento_maspy_final.py
# Sistema Multi-Agentes para Negociação em Cruzamento usando MASPY
# Baseado no exemplo de negociação do PDF (Sellers e Buyers)

from maspy import *
from random import randint

# ============================================================================
# AMBIENTE - CRUZAMENTO
# ============================================================================

class CruzamentoEnvironment(Environment):
    """Ambiente que representa um cruzamento - similar ao Website do exemplo"""

    # Action: Veículo anuncia intenção
    def anunciar_passagem(self, agt, proposta):
        """Veículo anuncia proposta - similar a announce_trip"""
        self.print(f"Veiculo {agt} anunciou: tipo={proposta['tipo']}, prioridade={proposta['prioridade']:.2f}")
        self.create(Percept("proposta", {
            "veiculo": agt,
            "tipo": proposta['tipo'],
            "prioridade": proposta['prioridade']
        }))

    # Action: Remover proposta
    def remover_proposta(self, agt, proposta):
        """Remove proposta - similar a delist_trip"""
        self.print(f"Proposta de {proposta['veiculo']} removida")
        self.delete(Percept("proposta", proposta))

# ============================================================================
# AGENTE - COORDENADOR (similar ao Seller)
# ============================================================================

class CoordenadorAgent(Agent):
    """Coordenador que gerencia permissões"""

    def __init__(self, agt_name=None):
        super().__init__(agt_name)
        self.add(Goal("avaliar"))  # Goal inicial

    # Plano: Avaliar propostas
    # Gatilho: Ganhar objetivo "avaliar"
    @pl(gain, Goal("avaliar"))
    def avaliar_propostas(self, src):
        """Avalia propostas e escolhe vencedor"""
        self.wait(1)  # Aguarda propostas chegarem

        # Busca todas as propostas
        propostas = self.get(Belief("proposta", "Dados"), all=True, ck_src=False)

        if propostas is None:
            self.print("Nenhuma proposta recebida")
            return

        self.print(f"\nAvaliando {len(propostas)} proposta(s)")

        # Escolhe por maior prioridade
        melhor_score = -1
        melhor_proposta = None

        for prop in propostas:
            assert isinstance(prop, Belief)
            dados = prop.args
            prioridade = dados['prioridade']

            self.print(f"  - {dados['veiculo']}: {dados['tipo']}, prioridade={prioridade:.2f}")

            if prioridade > melhor_score:
                melhor_score = prioridade
                melhor_proposta = dados

        if melhor_proposta:
            vencedor = melhor_proposta['veiculo']
            self.print(f"\n>>> VENCEDOR: {vencedor}")

            # Envia permissão
            self.send(vencedor, tell, Belief("permissao"))

            # Remove proposta do ambiente
            self.remover_proposta(melhor_proposta)

    # Plano: Confirmar travessia
    # Gatilho: Ganhar objetivo "atravessou(Veiculo)"
    @pl(gain, Goal("atravessou", "Veiculo"))
    def confirmar_travessia(self, src, veiculo_id):
        """Confirma que veículo atravessou"""
        self.print(f"Veiculo {veiculo_id} atravessou com sucesso!")

# ============================================================================
# AGENTE - VEÍCULO (similar ao Buyer)
# ============================================================================

class VeiculoAgent(Agent):
    """Agente veículo"""

    def __init__(self, agt_name, direcao, tipo='normal'):
        super().__init__(agt_name)
        self.add(Belief("direcao", direcao))
        self.add(Belief("tipo", tipo))
        self.add(Goal("tentar_passar"))  # Goal inicial

    # Plano: Enviar proposta
    # Gatilho: Ganhar objetivo "tentar_passar"
    # Contexto: Tem tipo e direção
    @pl(gain, Goal("tentar_passar"), Belief("tipo", "Tipo"))
    def enviar_proposta(self, src, tipo):
        """Envia proposta ao coordenador"""
        self.wait(0.5)  # Pequena espera

        # Calcula prioridade
        if tipo == 'emergencia':
            prioridade = 100.0 + randint(0, 10)
        else:
            prioridade = randint(1, 50) * 1.0

        proposta = {
            'veiculo_id': self.my_name,
            'tipo': tipo,
            'prioridade': prioridade
        }

        self.print(f"Enviando proposta: tipo={tipo}, prioridade={prioridade:.2f}")

        # Anuncia no ambiente
        self.anunciar_passagem(proposta)

        # Aguarda resposta
        # (o coordenador enviará belief "permissao" se aceito)

    # Plano: Receber permissão
    # Gatilho: Ganhar belief "permissao"
    @pl(gain, Belief("permissao"))
    def atravessar_cruzamento(self, src):
        """Atravessa após receber permissão"""
        tipo = self.get(Belief("tipo")).args
        tipo_str = "EMERGENCIA" if tipo == 'emergencia' else "Normal"

        self.print(f"[{tipo_str}] PERMISSAO recebida! Atravessando...")

        # Simula travessia
        tempo_travessia = 2.0 if tipo == 'emergencia' else 3.0
        self.wait(tempo_travessia)

        self.print(f"[{tipo_str}] Atravessei o cruzamento!")

        # Informa coordenador
        self.send("Coordenador", achieve, Goal("atravessou", self.my_name))

        self.stop_cycle()

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SMA CRUZAMENTO - NEGOCIACAO COM MASPY")
    print("="*60)

    # Cria ambiente
    cruzamento = CruzamentoEnvironment()

    # Cria coordenador
    coordenador = CoordenadorAgent("Coordenador")

    # Cria veículos
    veiculos = []

    # 1 emergência
    v1 = VeiculoAgent("V1_Ambulancia", "norte", tipo='emergencia')
    veiculos.append(v1)

    # 4 normais
    direcoes = ['sul', 'leste', 'oeste', 'norte']
    for i in range(2, 6):
        veiculo = VeiculoAgent(f"V{i}", direcoes[i-2], tipo='normal')
        veiculos.append(veiculo)

    print("\nConfiguracao:")
    print(f"  - Total: {len(veiculos)} veiculos")
    print(f"  - 1 EMERGENCIA (V1_Ambulancia)")
    print(f"  - 4 Normais (V2, V3, V4, V5)")

    print("\nIniciando sistema...")
    print("="*60)

    # Conecta agentes ao ambiente
    agent_list = [coordenador] + veiculos
    Admin().connect_to(agent_list, cruzamento)
    Admin().report = True

    # Inicia sistema
    Admin().start_system()

    print("\n" + "="*60)
    print("SIMULACAO CONCLUIDA")
    print("="*60)
