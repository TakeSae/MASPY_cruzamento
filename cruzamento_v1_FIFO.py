# cruzamento_teste.py
# Sistema de Cruzamento com Multi-Agentes

import time
from typing import Dict, List, Optional

class CruzamentoEnvironment:
    """
    Ambiente que representa um cruzamento de 4 vias
    Implementação standalone sem dependências externas
    """
    
    def __init__(self):
        # Estado do cruzamento
        self.ocupado = False
        self.veiculo_atual = None
        
        # Filas de espera por direção
        self.filas = {
            'norte': [],
            'sul': [],
            'leste': [],
            'oeste': []
        }
        
        # Histórico de passagens
        self.historico = []
        
        # Tempo de simulação
        self.tempo_atual = 0
        
    def adicionar_veiculo_fila(self, veiculo_id: str, direcao: str, tempo_chegada: float):
        """
        Adiciona um veículo à fila de espera
        """
        if direcao not in self.filas:
            raise ValueError(f"Direção inválida: {direcao}")
            
        self.filas[direcao].append({
            'id': veiculo_id,
            'tempo_chegada': tempo_chegada,
            'prioridade': 0
        })
        print(f"[{self.tempo_atual:.1f}s] Veículo {veiculo_id} entrou na fila da direção {direcao}")
        
    def remover_veiculo_fila(self, veiculo_id: str, direcao: str):
        """
        Remove um veículo da fila
        """
        self.filas[direcao] = [v for v in self.filas[direcao] 
                               if v['id'] != veiculo_id]
        
    def ocupar_cruzamento(self, veiculo_id: str) -> bool:
        """
        Marca o cruzamento como ocupado
        """
        if not self.ocupado:
            self.ocupado = True
            self.veiculo_atual = veiculo_id
            print(f"[{self.tempo_atual:.1f}s] Veículo {veiculo_id} OCUPOU o cruzamento")
            return True
        return False
        
    def liberar_cruzamento(self) -> Optional[str]:
        """
        Libera o cruzamento
        """
        self.ocupado = False
        anterior = self.veiculo_atual
        self.veiculo_atual = None
        
        if anterior:
            self.historico.append({
                'veiculo': anterior,
                'tempo_saida': self.tempo_atual
            })
            print(f"[{self.tempo_atual:.1f}s] Veículo {anterior} LIBEROU o cruzamento")
        
        return anterior
        
    def get_estado(self) -> Dict:
        """
        Retorna o estado atual do ambiente
        """
        return {
            'ocupado': self.ocupado,
            'veiculo_atual': self.veiculo_atual,
            'filas': {k: len(v) for k, v in self.filas.items()},
            'tempo': self.tempo_atual
        }
        
    def atualizar_tempo(self, delta_t: float = 1.0):
        """
        Avança o tempo de simulação
        """
        self.tempo_atual += delta_t
        
    def calcular_tempo_espera(self, veiculo_id: str, direcao: str) -> float:
        """
        Calcula tempo de espera de um veículo
        """
        for veiculo in self.filas[direcao]:
            if veiculo['id'] == veiculo_id:
                return self.tempo_atual - veiculo['tempo_chegada']
        return 0.0
    
    def mostrar_status(self):
        """
        Exibe o status atual do cruzamento
        """
        print(f"\n{'='*50}")
        print(f"TEMPO: {self.tempo_atual:.1f}s")
        print(f"Cruzamento: {'OCUPADO' if self.ocupado else 'LIVRE'}")
        if self.veiculo_atual:
            print(f"Veículo no cruzamento: {self.veiculo_atual}")
        
        print("\nFilas de espera:")
        for direcao, fila in self.filas.items():
            if fila:
                veiculos = [v['id'] for v in fila]
                print(f"  {direcao.upper()}: {veiculos}")
        print(f"{'='*50}\n")


class VeiculoAgente:
    """
    Agente que representa um veículo no cruzamento
    """
    
    def __init__(self, veiculo_id: str, direcao_origem: str, 
                 tempo_travessia: float = 3.0):
        self.id = veiculo_id
        self.direcao_origem = direcao_origem
        self.tempo_travessia = tempo_travessia
        self.estado = "esperando"  # esperando, atravessando, concluido
        self.tempo_inicio_travessia = None
        
    def solicitar_passagem(self, ambiente: CruzamentoEnvironment) -> bool:
        """
        Tenta solicitar passagem pelo cruzamento
        """
        if self.estado == "esperando":
            sucesso = ambiente.ocupar_cruzamento(self.id)
            if sucesso:
                self.estado = "atravessando"
                self.tempo_inicio_travessia = ambiente.tempo_atual
                ambiente.remover_veiculo_fila(self.id, self.direcao_origem)
                return True
        return False
    
    def atualizar(self, ambiente: CruzamentoEnvironment):
        """
        Atualiza o estado do veículo
        """
        if self.estado == "atravessando":
            tempo_decorrido = ambiente.tempo_atual - self.tempo_inicio_travessia
            
            if tempo_decorrido >= self.tempo_travessia:
                ambiente.liberar_cruzamento()
                self.estado = "concluido"


def simular_cruzamento():
    """
    Simulação principal do cruzamento
    """
    print("=== SIMULAÇÃO DE CRUZAMENTO COM MULTI-AGENTES ===\n")
    
    # Criar ambiente
    ambiente = CruzamentoEnvironment()
    
    # Criar veículos (agentes)
    veiculos = [
        VeiculoAgente("V1", "norte", tempo_travessia=3.0),
        VeiculoAgente("V2", "sul", tempo_travessia=2.5),
        VeiculoAgente("V3", "leste", tempo_travessia=3.5),
        VeiculoAgente("V4", "oeste", tempo_travessia=2.0),
        VeiculoAgente("V5", "norte", tempo_travessia=3.0),
    ]
    
    # Adicionar veículos às filas em tempos diferentes
    ambiente.adicionar_veiculo_fila("V1", "norte", 0.0)
    ambiente.adicionar_veiculo_fila("V2", "sul", 1.0)
    ambiente.adicionar_veiculo_fila("V3", "leste", 2.0)
    ambiente.adicionar_veiculo_fila("V4", "oeste", 4.0)
    ambiente.adicionar_veiculo_fila("V5", "norte", 5.0)
    
    # Simular por 20 segundos
    tempo_simulacao = 20.0
    dt = 0.5  # intervalo de atualização
    
    while ambiente.tempo_atual < tempo_simulacao:
        # Mostrar status a cada 2 segundos
        if int(ambiente.tempo_atual * 2) % 4 == 0:
            ambiente.mostrar_status()
        
        # Adicionar veículos à fila conforme o tempo
        for veiculo in veiculos:
            if veiculo.estado == "inicial":
                tempo_chegada = {'V1': 0.0, 'V2': 1.0, 'V3': 2.0, 
                                'V4': 4.0, 'V5': 5.0}.get(veiculo.id, 0.0)
                
                if ambiente.tempo_atual >= tempo_chegada:
                    veiculo.estado = "esperando"
        
        # Atualizar veículos que estão atravessando
        for veiculo in veiculos:
            veiculo.atualizar(ambiente)
        
        # Tentar dar passagem aos veículos em espera
        if not ambiente.ocupado:
            for direcao in ['norte', 'sul', 'leste', 'oeste']:
                if ambiente.filas[direcao]:
                    proximo_veiculo_id = ambiente.filas[direcao][0]['id']
                    proximo_veiculo = next((v for v in veiculos 
                                          if v.id == proximo_veiculo_id), None)
                    
                    if proximo_veiculo and proximo_veiculo.estado == "esperando":
                        if proximo_veiculo.solicitar_passagem(ambiente):
                            break
        
        # Avançar tempo
        ambiente.atualizar_tempo(dt)
        time.sleep(0.1)  # Para visualização
    
    # Resultado final
    print("\n=== SIMULAÇÃO CONCLUÍDA ===")
    print(f"\nVeículos que atravessaram: {len(ambiente.historico)}")
    for registro in ambiente.historico:
        print(f"  {registro['veiculo']} - Tempo de saída: {registro['tempo_saida']:.1f}s")


if __name__ == "__main__":
    simular_cruzamento()