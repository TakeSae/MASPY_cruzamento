# -*- coding: utf-8 -*-
"""Teste simplificado com apenas 2 experimentos"""

from maspy import *
import time

class CruzamentoEnvironment(Environment):
    def __init__(self):
        super().__init__()
        self.cruzamento_livre = True

class VeiculoAgent(Agent):
    def __init__(self, agt_name=None, tipo="carro", prioridade=10, coordenador="Coordenador_1"):
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
        self.print("\n=== DECIDINDO VENCEDOR ===")
        propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)

        if not propostas:
            self.print("ERRO: Sem propostas")
            self.stop_cycle()
            return

        melhor_prio = -1
        vencedor_id = None

        for prop in propostas:
            dados = prop.args
            if dados['prio'] > melhor_prio:
                melhor_prio = dados['prio']
                vencedor_id = dados['id']

        self.print(f">>> VENCEDOR: {vencedor_id} (prio={melhor_prio})")
        self.send(broadcast, tell, Belief("decisao", vencedor_id))
        self.stop_cycle()

def executar_experimento(numero, veiculos_config):
    print(f"\n{'='*60}")
    print(f"EXPERIMENTO {numero}")
    print('='*60)

    env = CruzamentoEnvironment()
    coord_name = f"Coordenador_{numero}"
    coord = CoordenadorAgent(coord_name, num_veiculos=len(veiculos_config))

    veiculos = []
    for v in veiculos_config:
        veiculo = VeiculoAgent(
            f"{v['nome']}_exp{numero}",
            tipo=v['tipo'],
            prioridade=v['prioridade'],
            coordenador=coord_name
        )
        veiculos.append(veiculo)

    admin = Admin()
    admin.connect_to([coord] + veiculos, env)
    admin.start_system()

    time.sleep(1.5)

    print(f"EXPERIMENTO {numero} CONCLUIDO\n")

if __name__ == "__main__":
    print("TESTE COM 2 EXPERIMENTOS")

    # Experimento 1
    executar_experimento(1, [
        {'nome': 'Carro1', 'tipo': 'carro', 'prioridade': 10},
        {'nome': 'Ambulancia', 'tipo': 'ambulancia', 'prioridade': 100}
    ])

    print("\n>>> Aguardando antes do proximo experimento...\n")
    time.sleep(1)

    # Experimento 2
    executar_experimento(2, [
        {'nome': 'Moto1', 'tipo': 'moto', 'prioridade': 5},
        {'nome': 'Onibus1', 'tipo': 'onibus', 'prioridade': 30}
    ])

    print("\n" + "="*60)
    print("AMBOS EXPERIMENTOS CONCLUIDOS!")
    print("="*60)
