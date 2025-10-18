# -*- coding: utf-8 -*-
"""
Testes Individuais - Execute UM experimento por vez
====================================================

IMPORTANTE: Devido a limitações do MASPY, execute apenas UM teste
por execução do script.

USO:
  python teste_individual.py 1    # Executa experimento 1
  python teste_individual.py 2    # Executa experimento 2
  ... e assim por diante
"""

from maspy import *
import sys

class CruzamentoEnvironment(Environment):
    def __init__(self):
        super().__init__()

class VeiculoAgent(Agent):
    def __init__(self, agt_name=None, tipo="carro", prioridade=10):
        super().__init__(agt_name)
        self.tipo = tipo
        self.prioridade = prioridade
        self.add(Goal("atravessar"))

    @pl(gain, Goal("atravessar"))
    def enviar_proposta(self, src):
        proposta = {'id': self.my_name, 'tipo': self.tipo, 'prio': self.prioridade}
        self.print(f"Proposta: tipo={self.tipo}, prio={self.prioridade}")
        self.send("Coordenador_1", tell, Belief("proposta", proposta))

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        if vencedor == self.my_name:
            self.print(f">>> VENCI!")
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
        self.print(f"Recebi: {dados['id']} (tipo={dados['tipo']}, prio={dados['prio']})")
        self.contador_propostas += 1
        if self.contador_propostas >= self.num_veiculos:
            self.add(Goal("decidir"))

    @pl(gain, Goal("decidir"))
    def decidir_vencedor(self, src):
        self.print("\n" + "="*60)
        self.print("AVALIANDO PROPOSTAS")
        self.print("="*60)

        propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)
        if not propostas:
            self.print("ERRO: Sem propostas")
            self.stop_cycle()
            return

        melhor_prio = -1
        vencedor_dados = None

        for prop in propostas:
            dados = prop.args
            self.print(f"  - {dados['id']}: {dados['tipo']} (prio={dados['prio']})")
            if dados['prio'] > melhor_prio:
                melhor_prio = dados['prio']
                vencedor_dados = dados

        self.print("\n" + "="*60)
        self.print(f">>> VENCEDOR: {vencedor_dados['id']}")
        self.print(f"    Tipo: {vencedor_dados['tipo']}")
        self.print(f"    Prioridade: {vencedor_dados['prio']}")
        self.print("="*60 + "\n")

        self.send(broadcast, tell, Belief("decisao", vencedor_dados['id']))
        self.stop_cycle()

def experimento_1():
    """Exp 1: Cenario base - ambulancia vs normais"""
    print("\n" + "="*70)
    print("EXPERIMENTO 1: Cenario Base")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=4)
    v1 = VeiculoAgent("Carro1", "carro", 10)
    v2 = VeiculoAgent("Ambulancia", "ambulancia", 100)
    v3 = VeiculoAgent("Moto1", "moto", 5)
    v4 = VeiculoAgent("Onibus1", "onibus", 30)

    Admin().connect_to([coord, v1, v2, v3, v4], env)
    Admin().start_system()

def experimento_2():
    """Exp 2: Multiplas emergencias"""
    print("\n" + "="*70)
    print("EXPERIMENTO 2: Multiplas Emergencias")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=4)
    v1 = VeiculoAgent("Ambulancia1", "ambulancia", 100)
    v2 = VeiculoAgent("Ambulancia2", "ambulancia", 95)
    v3 = VeiculoAgent("Bombeiros", "bombeiros", 98)
    v4 = VeiculoAgent("Carro1", "carro", 10)

    Admin().connect_to([coord, v1, v2, v3, v4], env)
    Admin().start_system()

def experimento_3():
    """Exp 3: Prioridades iguais"""
    print("\n" + "="*70)
    print("EXPERIMENTO 3: Prioridades Iguais")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=4)
    v1 = VeiculoAgent("Carro1", "carro", 10)
    v2 = VeiculoAgent("Carro2", "carro", 10)
    v3 = VeiculoAgent("Carro3", "carro", 10)
    v4 = VeiculoAgent("Carro4", "carro", 10)

    Admin().connect_to([coord, v1, v2, v3, v4], env)
    Admin().start_system()

def experimento_4():
    """Exp 4: Cargas pesadas"""
    print("\n" + "="*70)
    print("EXPERIMENTO 4: Cargas Pesadas")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=4)
    v1 = VeiculoAgent("Caminhao1", "caminhao", 50)
    v2 = VeiculoAgent("Onibus1", "onibus", 40)
    v3 = VeiculoAgent("Moto1", "moto", 5)
    v4 = VeiculoAgent("Carro1", "carro", 10)

    Admin().connect_to([coord, v1, v2, v3, v4], env)
    Admin().start_system()

def experimento_5():
    """Exp 5: Cenario misto com 6 veiculos"""
    print("\n" + "="*70)
    print("EXPERIMENTO 5: Cenario Misto (6 veiculos)")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=6)
    v1 = VeiculoAgent("Moto1", "moto", 5)
    v2 = VeiculoAgent("Carro1", "carro", 15)
    v3 = VeiculoAgent("Onibus1", "onibus", 35)
    v4 = VeiculoAgent("Caminhao1", "caminhao", 45)
    v5 = VeiculoAgent("Taxi1", "taxi", 20)
    v6 = VeiculoAgent("Ambulancia", "ambulancia", 100)

    Admin().connect_to([coord, v1, v2, v3, v4, v5, v6], env)
    Admin().start_system()

def experimento_6():
    """Exp 6: Teste de estresse com 10 veiculos"""
    print("\n" + "="*70)
    print("EXPERIMENTO 6: Teste de Estresse (10 veiculos)")
    print("="*70 + "\n")

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=10)

    veiculos = [
        VeiculoAgent(f"Veiculo{i}", "carro", i*10)
        for i in range(1, 11)
    ]

    Admin().connect_to([coord] + veiculos, env)
    Admin().start_system()

if __name__ == "__main__":
    experimentos = {
        '1': experimento_1,
        '2': experimento_2,
        '3': experimento_3,
        '4': experimento_4,
        '5': experimento_5,
        '6': experimento_6,
    }

    if len(sys.argv) < 2:
        print("\nUSO: python teste_individual.py [1-6]")
        print("\nExperimentos disponiveis:")
        print("  1 - Cenario Base (ambulancia vs normais)")
        print("  2 - Multiplas Emergencias")
        print("  3 - Prioridades Iguais")
        print("  4 - Cargas Pesadas")
        print("  5 - Cenario Misto (6 veiculos)")
        print("  6 - Teste de Estresse (10 veiculos)")
        print("\nExemplo: python teste_individual.py 1\n")
        sys.exit(1)

    num_exp = sys.argv[1]

    if num_exp not in experimentos:
        print(f"\nERRO: Experimento '{num_exp}' invalido. Use 1-6.\n")
        sys.exit(1)

    experimentos[num_exp]()

    print("\n" + "="*70)
    print(f"EXPERIMENTO {num_exp} CONCLUIDO")
    print("="*70 + "\n")
