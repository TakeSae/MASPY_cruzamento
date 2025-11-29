from maspy import *
import time

# CLASSES DO SISTEMA (Importadas do arquivo principal)

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
        self.print(f"Veiculo {veiculo_id} chegou (tipo={tipo}, prio={prioridade})")

    def iniciar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = False
        self.veiculo_atravessando = veiculo_id
        self.print(f">>> {veiculo_id} atravessando")

    def finalizar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = True
        self.veiculo_atravessando = None
        self.print(f"{veiculo_id} concluiu travessia")

class VeiculoAgent(Agent):

    def __init__(self, agt_name=None, tipo="carro", prioridade=10, coordenador="Coordenador"):
        super().__init__(agt_name)
        self.tipo = tipo
        self.prioridade = prioridade
        self.coordenador = coordenador
        self.add(Goal("atravessar"))

    @pl(gain, Goal("atravessar"))
    def enviar_proposta(self, src):
        proposta = {
            'id': self.my_name,
            'tipo': self.tipo,
            'prio': self.prioridade
        }
        self.print(f"Proposta: tipo={self.tipo}, prio={self.prioridade}")
        self.send(self.coordenador, tell, Belief("proposta", proposta))

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        if vencedor == self.my_name:
            self.print(f">>> VENCI! Atravessando...")
        else:
            self.print(f"Aguardando ({vencedor} venceu)")
        self.stop_cycle()

class CoordenadorAgent(Agent):

    def __init__(self, agt_name=None, num_veiculos=4):
        super().__init__(agt_name)
        self.num_veiculos = num_veiculos
        self.contador_propostas = 0

    @pl(gain, Belief("proposta", Any))
    def coletar_propostas(self, src, dados):
        self.print(f"Recebi de {src}: {dados['tipo']}, prio={dados['prio']}")
        self.contador_propostas += 1
        if self.contador_propostas >= self.num_veiculos:
            self.add(Goal("decidir"))

    @pl(gain, Goal("decidir"))
    def decidir_vencedor(self, src):
        self.print("\n" + "="*50)
        self.print("AVALIANDO PROPOSTAS")
        self.print("="*50)

        propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)

        if not propostas:
            self.print("ERRO: Sem propostas")
            self.stop_cycle()
            return

        self.print(f"\nTotal: {len(propostas)} propostas")

        melhor_prio = -1
        vencedor_id = None
        vencedor_dados = None

        for prop in propostas:
            dados = prop.args
            self.print(f"  - {dados['id']}: {dados['tipo']} (prio={dados['prio']})")
            if dados['prio'] > melhor_prio:
                melhor_prio = dados['prio']
                vencedor_id = dados['id']
                vencedor_dados = dados

        self.print("\n" + "="*50)
        self.print(f">>> VENCEDOR: {vencedor_dados['id']}")
        self.print(f"    Tipo: {vencedor_dados['tipo']}")
        self.print(f"    Prioridade: {vencedor_dados['prio']}")
        self.print("="*50 + "\n")

        self.send(broadcast, tell, Belief("decisao", vencedor_id))
        self.stop_cycle()

# FUNCOES AUXILIARES

def limpar_sistema():
    time.sleep(0.3)

def executar_experimento(numero, descricao, veiculos_config):

    print("\n" + "="*80)
    print(f"EXPERIMENTO {numero}: {descricao}")
    print("="*80)

    print("\nVeiculos participantes:")
    for v in veiculos_config:
        print(f"  - {v['nome']}: {v['tipo']} (prioridade={v['prioridade']})")

    print("\nIniciando negociacao...\n")
    print("-"*80 + "\n")

    env = CruzamentoEnvironment()

    coord_name = "Coordenador"
    coord = CoordenadorAgent(coord_name, num_veiculos=len(veiculos_config))

    veiculos = []
    for v_config in veiculos_config:
        veiculo_name = v_config['nome']
        veiculo = VeiculoAgent(
            veiculo_name,
            tipo=v_config['tipo'],
            prioridade=v_config['prioridade'],
            coordenador=coord_name
        )
        veiculos.append(veiculo)

    admin = Admin()
    admin.connect_to([coord] + veiculos, env)
    admin.start_system()

    print("\n" + "-"*80)
    print(f"EXPERIMENTO {numero} CONCLUIDO")
    print("="*80 + "\n")

    limpar_sistema()

# EXPERIMENTOS

def experimento_1_base():
    """Experimento 1: Cenario base - 1 emergencia vs 3 normais"""
    veiculos = [
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prioridade': 100},
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 30}
    ]
    executar_experimento(
        1,
        "Cenario Base - Ambulancia deve vencer",
        veiculos
    )

def experimento_2_multiplas_emergencias():
    """Experimento 2: Multiplas emergencias competindo"""
    veiculos = [
        {'nome': 'Ambulancia1', 'tipo': 'ambulancia', 'prioridade': 100},
        {'nome': 'Ambulancia2', 'tipo': 'ambulancia', 'prioridade': 95},
        {'nome': 'Bombeiros', 'tipo': 'bombeiros', 'prioridade': 98},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10}
    ]
    executar_experimento(
        2,
        "Multiplas Emergencias - Ambulancia1 (prio=100) deve vencer",
        veiculos
    )

def experimento_3_prioridades_iguais():
    """Experimento 3: Todos com mesma prioridade"""
    veiculos = [
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro2', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro3', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro4', 'tipo': 'carro', 'prioridade': 10}
    ]
    executar_experimento(
        3,
        "Prioridades Iguais - Primeiro a ser processado vence",
        veiculos
    )

def experimento_4_cargas_pesadas():
    """Experimento 4: Veiculos de carga vs leves"""
    veiculos = [
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prioridade': 50},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 40},
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10}
    ]
    executar_experimento(
        4,
        "Cargas Pesadas - Caminhao (prio=50) deve vencer",
        veiculos
    )

def experimento_5_misto():
    """Experimento 5: Cenario misto com 6 veiculos"""
    veiculos = [
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 15},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 35},
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prioridade': 45},
        {'nome': 'Taxi1', 'tipo': 'taxi', 'prioridade': 20},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prioridade': 100}
    ]
    executar_experimento(
        5,
        "Cenario Misto (6 veiculos) - Ambulancia deve vencer",
        veiculos
    )

def experimento_6_estresse():
    """Experimento 6: Teste de estresse com 10 veiculos"""
    veiculos = [
        {'nome': f'Veiculo{i}', 'tipo': 'carro', 'prioridade': i*10}
        for i in range(1, 11)
    ]
    executar_experimento(
        6,
        "Teste de Estresse (10 veiculos) - Veiculo10 (prio=100) deve vencer",
        veiculos
    )

# EXECUCAO PRINCIPAL

if __name__ == "__main__":
    print("\nEste script define 6 experimentos diferentes para demonstrar")
    print("todas as possibilidades de negociacao do sistema.")
    print("\nPara executar os experimentos:")
    print("  1. Execute um experimento especifico:")
    print("     python -c \"from experimentos_cruzamento import experimento_1_base; experimento_1_base()\"")
    print("\n  2. OU execute todos usando o script shell:")
    print("     ./run_all_experiments.sh")
    print("\nExperimentos disponiveis:")
    print("  - experimento_1_base()")
    print("  - experimento_2_multiplas_emergencias()")
    print("  - experimento_3_prioridades_iguais()")
    print("  - experimento_4_cargas_pesadas()")
    print("  - experimento_5_misto()")
    print("  - experimento_6_estresse()")
    print("\n" + "="*80)
