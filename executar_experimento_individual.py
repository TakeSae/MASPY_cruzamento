# -*- coding: utf-8 -*-
"""Executa um único experimento - chamado pelo script principal"""

import sys
from maspy import *
import time

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
        self.print(f"Proposta: {self.tipo}, prio={self.prioridade}")
        self.send("Coordenador", tell, Belief("proposta", proposta))

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        if vencedor == self.my_name:
            self.print(f">>> VENCI!")
        else:
            self.print(f"Perdeu para {vencedor}")
        self.stop_cycle()

class CoordenadorAgent(Agent):
    def __init__(self, agt_name=None, num_veiculos=4):
        super().__init__(agt_name)
        self.num_veiculos = num_veiculos
        self.contador = 0

    @pl(gain, Belief("proposta", Any))
    def coletar(self, src, dados):
        self.print(f"Recebi: {dados['tipo']}, prio={dados['prio']}")
        self.contador += 1
        if self.contador >= self.num_veiculos:
            self.add(Goal("decidir"))

    @pl(gain, Goal("decidir"))
    def decidir(self, src):
        propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)
        melhor = max(propostas, key=lambda p: p.args['prio'])
        vencedor = melhor.args['id']
        self.print(f">>> VENCEDOR: {vencedor} (prio={melhor.args['prio']})")
        self.send(broadcast, tell, Belief("decisao", vencedor))
        self.stop_cycle()

# Configurações dos experimentos
EXPERIMENTOS = {
    1: [
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prioridade': 100},
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 30}
    ],
    2: [
        {'nome': 'Ambulancia1', 'tipo': 'ambulancia', 'prioridade': 100},
        {'nome': 'Ambulancia2', 'tipo': 'ambulancia', 'prioridade': 95},
        {'nome': 'Bombeiros', 'tipo': 'bombeiros', 'prioridade': 98},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10}
    ],
    3: [
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro2', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro3', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Carro4', 'tipo': 'carro', 'prioridade': 10}
    ],
    4: [
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prioridade': 50},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 40},
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10}
    ],
    5: [
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 15},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 35},
        {'nome': 'Caminhao1', 'tipo': 'caminhao', 'prioridade': 45},
        {'nome': 'Taxi1', 'tipo': 'taxi', 'prioridade': 20},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prioridade': 100}
    ],
    6: [
        {'nome': f'Veiculo{i}', 'tipo': 'carro', 'prioridade': i*10}
        for i in range(1, 11)
    ]
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python executar_experimento_individual.py <numero_experimento>")
        sys.exit(1)

    num_exp = int(sys.argv[1])

    if num_exp not in EXPERIMENTOS:
        print(f"Experimento {num_exp} não encontrado")
        sys.exit(1)

    veiculos_config = EXPERIMENTOS[num_exp]

    print(f"\n{'='*60}")
    print(f"EXPERIMENTO {num_exp}")
    print('='*60)

    env = CruzamentoEnvironment()
    coord = CoordenadorAgent("Coordenador", num_veiculos=len(veiculos_config))

    veiculos = []
    for v in veiculos_config:
        veiculos.append(VeiculoAgent(v['nome'], tipo=v['tipo'], prioridade=v['prioridade']))

    Admin().connect_to([coord] + veiculos, env)
    Admin().start_system()

    print(f"\nExperimento {num_exp} finalizado")
