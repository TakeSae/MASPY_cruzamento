from maspy import *

# AMBIENTE - CRUZAMENTO
class CruzamentoEnvironment(Environment):

    def __init__(self):
        super().__init__()
        self.cruzamento_livre = True
        self.veiculos_aguardando = []
        self.veiculo_atravessando = None

    def registrar_chegada(self, agt, veiculo_id, tipo, prioridade):
        self.veiculos_aguardando.append({
            'id': veiculo_id,
            'tipo': tipo,
            'prioridade': prioridade
        })
        self.print(f"Veiculo {veiculo_id} chegou ao cruzamento (tipo={tipo}, prio={prioridade})")

    def iniciar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = False
        self.veiculo_atravessando = veiculo_id
        self.print(f">>> {veiculo_id} iniciou a travessia do cruzamento")

    def finalizar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = True
        self.veiculo_atravessando = None
        self.print(f"{veiculo_id} finalizou a travessia. Cruzamento livre.")

# AGENTE VEICULO
class VeiculoAgent(Agent):

    def __init__(self, agt_name=None, tipo="carro", prioridade=10):
        super().__init__(agt_name)
        self.tipo = tipo
        self.prioridade = prioridade
        self.add(Goal("atravessar"))

    @pl(gain, Goal("atravessar"))
    def enviar_proposta(self, src):
        proposta = {
            'id': self.my_name,
            'tipo': self.tipo,
            'prio': self.prioridade
        }

        self.print(f"Enviando proposta: tipo={self.tipo}, prioridade={self.prioridade}")
        self.send("Coordenador_1", tell, Belief("proposta", proposta))

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        if vencedor == self.my_name:
            self.print(f">>> GANHEI! Atravessando o cruzamento...")
        else:
            self.print(f"Aguardando. Vencedor: {vencedor}")

        self.stop_cycle()

# AGENTE COORDENADOR
class CoordenadorAgent(Agent):

    def __init__(self, agt_name=None, num_veiculos=4):
        super().__init__(agt_name)
        self.num_veiculos = num_veiculos
        self.contador_propostas = 0

    @pl(gain, Belief("proposta", Any))
    def coletar_propostas(self, src, dados):
        self.print(f"Proposta recebida de {src}: tipo={dados['tipo']}, prioridade={dados['prio']}")
        self.contador_propostas += 1

        if self.contador_propostas >= self.num_veiculos:
            self.add(Goal("decidir"))

    @pl(gain, Goal("decidir"))
    def decidir_vencedor(self, src):
        self.print("\n" + "="*60)
        self.print("AVALIANDO PROPOSTAS")
        self.print("="*60)

        propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)

        if not propostas or len(propostas) == 0:
            self.print("ERRO: Nenhuma proposta encontrada!")
            self.stop_cycle()
            return

        self.print(f"\nTotal de propostas: {len(propostas)}")

        melhor_prioridade = -1
        vencedor_id = None
        vencedor_dados = None

        for prop in propostas:
            dados = prop.args
            self.print(f"  - {dados['id']}: {dados['tipo']} (prioridade={dados['prio']})")

            if dados['prio'] > melhor_prioridade:
                melhor_prioridade = dados['prio']
                vencedor_id = dados['id']
                vencedor_dados = dados

        self.print("\n" + "="*60)
        self.print(f">>> VENCEDOR: {vencedor_dados['id']} <<<")
        self.print(f"  Tipo: {vencedor_dados['tipo']}")
        self.print(f"  Prioridade: {vencedor_dados['prio']}")
        self.print("="*60 + "\n")

        self.send(broadcast, tell, Belief("decisao", vencedor_id))

        self.stop_cycle()

# EXECUCAO PRINCIPAL

if __name__ == "__main__":
    print("="*70)
    print("SISTEMA MULTI-AGENTES DE NEGOCIACAO EM CRUZAMENTO")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*70)

    print("\nConfiguracao do Sistema:")
    print("  - 1 Coordenador")
    print("  - 4 Veiculos")
    print("\n  Veiculos:")
    print("    - Veiculo1: carro (prioridade=10)")
    print("    - Veiculo2: ambulancia (prioridade=100) [EMERGENCIA]")
    print("    - Veiculo3: onibus (prioridade=30)")
    print("    - Veiculo4: moto (prioridade=5)")

    print("\n  Protocolo de Negociacao:")
    print("    1. Veiculos enviam propostas ao Coordenador")
    print("    2. Coordenador coleta todas as propostas")
    print("    3. Coordenador avalia e decide por maior prioridade")
    print("    4. Coordenador notifica todos os veiculos (broadcast)")
    print("    5. Todos os agentes param seus ciclos\n")

    print("="*70 + "\n")

    coord = CoordenadorAgent("Coordenador", num_veiculos=4)

    v1 = VeiculoAgent("Veiculo1", tipo="carro", prioridade=10)
    v2 = VeiculoAgent("Veiculo2", tipo="ambulancia", prioridade=100)
    v3 = VeiculoAgent("Veiculo3", tipo="onibus", prioridade=30)
    v4 = VeiculoAgent("Veiculo4", tipo="moto", prioridade=5)

    env = CruzamentoEnvironment()

    Admin().connect_to([coord, v1, v2, v3, v4], env)

    Admin().start_system()

    print("\n" + "="*70)
    print("SISTEMA ENCERRADO COM SUCESSO")
    print("="*70)
