# cruzamento_completo.py
# Sistema Multi-Agentes para Negociação em Cruzamento
# Implementação completa para o Trabalho 1

import time
import random
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ============================================================================
# PROTOCOLO DE NEGOCIAÇÃO
# ============================================================================

class TipoMensagem(Enum):
    """Tipos de mensagens do protocolo"""
    ANUNCIO = "anuncio"
    PROPOSTA = "proposta"
    PERMISSAO = "permissao"
    NEGACAO = "negacao"
    CONCLUSAO = "conclusao"

class ProtocoloNegociacao:
    """
    Protocolo de negociação baseado em leilão com prioridades
    
    Fases:
    1. Anúncio: Veículos anunciam intenção de passar
    2. Proposta: Veículos enviam propostas com prioridades
    3. Avaliação: Coordenador avalia propostas
    4. Decisão: Coordenador concede permissão
    5. Execução: Veículo autorizado atravessa
    """
    
    def __init__(self):
        self.mensagens = []
        self.fase_atual = "anuncio"
        
    def criar_mensagem(self, tipo: TipoMensagem, remetente: str, 
                       destinatario: str = None, conteudo: Dict = None) -> Dict:
        """Cria uma mensagem do protocolo"""
        mensagem = {
            'tipo': tipo.value,
            'remetente': remetente,
            'destinatario': destinatario or 'broadcast',
            'conteudo': conteudo or {},
            'timestamp': time.time()
        }
        self.mensagens.append(mensagem)
        return mensagem
    
    def processar_mensagem(self, mensagem: Dict) -> str:
        """Processa uma mensagem recebida"""
        return mensagem['tipo']
    
    def limpar_mensagens(self):
        """Limpa buffer de mensagens"""
        self.mensagens = []

# ============================================================================
# AMBIENTE
# ============================================================================

class CruzamentoEnvironment:
    """
    Ambiente que representa um cruzamento de 4 vias
    """
    
    def __init__(self):
        self.ocupado = False
        self.veiculo_atual = None
        self.filas = {
            'norte': [],
            'sul': [],
            'leste': [],
            'oeste': []
        }
        self.historico = []
        self.tempo_atual = 0.0
        
    def adicionar_veiculo_fila(self, veiculo_id: str, direcao: str, 
                               tempo_chegada: float, tipo: str = 'normal'):
        """Adiciona um veículo à fila de espera"""
        if direcao not in self.filas:
            raise ValueError(f"Direção inválida: {direcao}")
            
        self.filas[direcao].append({
            'id': veiculo_id,
            'tempo_chegada': tempo_chegada,
            'tipo': tipo,
            'prioridade': 0
        })
        
        print(f"[{self.tempo_atual:.1f}s] Veiculo {veiculo_id} ({tipo}) entrou na fila {direcao.upper()}")
        
    def remover_veiculo_fila(self, veiculo_id: str, direcao: str):
        """Remove um veículo da fila"""
        self.filas[direcao] = [v for v in self.filas[direcao] 
                               if v['id'] != veiculo_id]
        
    def ocupar_cruzamento(self, veiculo_id: str) -> bool:
        """Marca o cruzamento como ocupado"""
        if not self.ocupado:
            self.ocupado = True
            self.veiculo_atual = veiculo_id
            return True
        return False
        
    def liberar_cruzamento(self) -> Optional[str]:
        """Libera o cruzamento"""
        self.ocupado = False
        anterior = self.veiculo_atual
        self.veiculo_atual = None
        
        if anterior:
            self.historico.append({
                'veiculo': anterior,
                'tempo_saida': self.tempo_atual
            })
        
        return anterior
        
    def get_estado(self) -> Dict:
        """Retorna o estado atual do ambiente"""
        return {
            'ocupado': self.ocupado,
            'veiculo_atual': self.veiculo_atual,
            'filas': self.filas.copy(),
            'tempo': self.tempo_atual
        }
        
    def atualizar_tempo(self, delta_t: float = 1.0):
        """Avança o tempo de simulação"""
        self.tempo_atual += delta_t
        
    def calcular_tempo_espera(self, veiculo_id: str, direcao: str) -> float:
        """Calcula tempo de espera de um veículo"""
        for veiculo in self.filas[direcao]:
            if veiculo['id'] == veiculo_id:
                return self.tempo_atual - veiculo['tempo_chegada']
        return 0.0
    
    def mostrar_status(self):
        """Exibe o status atual do cruzamento"""
        print(f"\n{'='*60}")
        print(f"TEMPO: {self.tempo_atual:.1f}s")
        print(f"Cruzamento: {'OCUPADO' if self.ocupado else 'LIVRE'}")
        if self.veiculo_atual:
            print(f"   Veiculo atual: {self.veiculo_atual}")
        
        print("\nFilas de espera:")
        total_espera = 0
        for direcao, fila in self.filas.items():
            if fila:
                veiculos = [f"{v['id']}({v['tipo'][0].upper()})" for v in fila]
                print(f"   {direcao.upper():6} -> {', '.join(veiculos)}")
                total_espera += len(fila)
        
        if total_espera == 0:
            print(f"   (Todas vazias)")
        print(f"{'='*60}")

# ============================================================================
# AGENTE VEÍCULO
# ============================================================================

class VeiculoAgent:
    """
    Agente que representa um veículo autônomo
    """
    
    def __init__(self, agent_id: str, direcao_origem: str, 
                 tipo: str = 'normal', tempo_travessia: float = 3.0):
        self.agent_id = agent_id
        self.direcao_origem = direcao_origem
        self.tipo = tipo  # 'normal' ou 'emergencia'
        self.tempo_travessia = tempo_travessia
        self.tempo_chegada = None
        self.tempo_espera = 0.0
        
        # Estados: aguardando, negociando, atravessando, concluido
        self.estado = 'aguardando'
        self.proposta_enviada = False
        self.permissao_recebida = False
        self.tempo_inicio_travessia = None
        
    def perceber(self, environment: CruzamentoEnvironment) -> Dict:
        """Percebe o estado do ambiente"""
        estado = environment.get_estado()
        self.tempo_espera = environment.calcular_tempo_espera(
            self.agent_id, 
            self.direcao_origem
        )
        return estado
        
    def calcular_prioridade(self) -> float:
        """
        Calcula prioridade dinâmica baseada em tempo de espera e tipo
        
        Fórmula: prioridade = tempo_espera * 0.1 + bonus_emergencia + random
        """
        prioridade_tempo = self.tempo_espera * 0.1
        bonus_emergencia = 100.0 if self.tipo == 'emergencia' else 0.0
        fator_aleatorio = random.uniform(0, 0.5)
        
        return prioridade_tempo + bonus_emergencia + fator_aleatorio
        
    def criar_proposta(self, estado_ambiente: Dict) -> Dict:
        """Cria uma proposta de passagem"""
        return {
            'veiculo_id': self.agent_id,
            'direcao': self.direcao_origem,
            'prioridade': self.calcular_prioridade(),
            'tempo_espera': self.tempo_espera,
            'tipo': self.tipo,
            'timestamp': estado_ambiente['tempo']
        }
        
    def decidir_acao(self, environment: CruzamentoEnvironment) -> str:
        """Decide a próxima ação baseada no estado"""
        estado = self.perceber(environment)
        
        if self.estado == 'aguardando':
            if not estado['ocupado']:
                self.estado = 'negociando'
                return 'iniciar_negociacao'
                
        elif self.estado == 'negociando':
            if self.permissao_recebida:
                return 'atravessar'
            else:
                return 'aguardar'
                
        elif self.estado == 'atravessando':
            tempo_decorrido = environment.tempo_atual - self.tempo_inicio_travessia
            if tempo_decorrido >= self.tempo_travessia:
                return 'sair_cruzamento'
            
        return 'aguardar'
        
    def executar_acao(self, acao: str, environment: CruzamentoEnvironment) -> bool:
        """Executa a ação decidida"""
        if acao == 'atravessar':
            # IMPORTANTE: Salvar tempo de espera ANTES de remover da fila
            self.tempo_espera = environment.calcular_tempo_espera(
                self.agent_id, 
                self.direcao_origem
            )
            
            sucesso = environment.ocupar_cruzamento(self.agent_id)
            if sucesso:
                self.estado = 'atravessando'
                self.tempo_inicio_travessia = environment.tempo_atual
                environment.remover_veiculo_fila(self.agent_id, self.direcao_origem)
                tipo_str = "EMERGENCIA" if self.tipo == 'emergencia' else "Normal"
                print(f"   [{tipo_str}] {self.agent_id} ATRAVESSANDO o cruzamento...")
            return sucesso
            
        elif acao == 'sair_cruzamento':
            environment.liberar_cruzamento()
            self.estado = 'concluido'
            tipo_str = "EMERGENCIA" if self.tipo == 'emergencia' else "Normal"
            print(f"   [{tipo_str}] {self.agent_id} LIBEROU o cruzamento")
            return True
            
        return False

# ============================================================================
# AGENTE COORDENADOR
# ============================================================================

class CoordenadorAgent:
    """
    Agente coordenador que gerencia o protocolo de negociação
    """
    
    def __init__(self, agent_id: str = 'coordenador'):
        self.agent_id = agent_id
        self.propostas_ativas = []
        self.historico_decisoes = []
        
    def registrar_proposta(self, proposta: Dict):
        """Registra uma nova proposta de passagem"""
        self.propostas_ativas.append(proposta)
        tipo_str = "EMERG" if proposta['tipo'] == 'emergencia' else "Normal"
        print(f"   [{tipo_str}] {proposta['veiculo_id']}: prioridade={proposta['prioridade']:.2f}, "
              f"espera={proposta['tempo_espera']:.1f}s")
        
    def avaliar_propostas(self) -> Optional[Dict]:
        """
        Avalia todas as propostas e decide qual veículo pode passar
        
        Critérios (em ordem de prioridade):
        1. Veículos de emergência têm prioridade absoluta
        2. Entre veículos normais, prioriza por tempo de espera
        3. Em caso de empate, usa timestamp de chegada
        """
        if not self.propostas_ativas:
            return None
            
        print(f"\n   Coordenador avaliando {len(self.propostas_ativas)} propostas...")
        
        # Separa veículos de emergência
        emergencias = [p for p in self.propostas_ativas if p['tipo'] == 'emergencia']
        normais = [p for p in self.propostas_ativas if p['tipo'] == 'normal']
        
        # Prioriza emergências
        if emergencias:
            vencedor = max(emergencias, key=lambda p: -p['timestamp'])
            print(f"   >> EMERGENCIA detectada! Prioridade maxima.")
        else:
            # Entre normais, escolhe por prioridade
            vencedor = max(normais, key=lambda p: (p['prioridade'], -p['timestamp']))
            print(f"   >> Aplicando criterio: maior tempo de espera")
            
        return vencedor
        
    def conceder_permissao(self, veiculo_id: str) -> Dict:
        """Concede permissão para um veículo atravessar"""
        decisao = {
            'tipo': 'permissao',
            'veiculo_autorizado': veiculo_id,
            'veiculos_negados': [p['veiculo_id'] for p in self.propostas_ativas 
                                if p['veiculo_id'] != veiculo_id],
            'timestamp': time.time()
        }
        
        self.historico_decisoes.append(decisao)
        
        print(f"   >> PERMISSAO concedida para: {veiculo_id}")
        if decisao['veiculos_negados']:
            print(f"   >> Negados: {', '.join(decisao['veiculos_negados'])}")
        
        return decisao
        
    def limpar_propostas(self):
        """Remove propostas processadas"""
        self.propostas_ativas = []
        
    def coordenar_rodada(self) -> Optional[Dict]:
        """
        Executa uma rodada completa de coordenação
        """
        if not self.propostas_ativas:
            return None
            
        # Avalia propostas
        proposta_vencedora = self.avaliar_propostas()
        
        if proposta_vencedora:
            # Concede permissão
            decisao = self.conceder_permissao(proposta_vencedora['veiculo_id'])
            
            # Limpa propostas para próxima rodada
            self.limpar_propostas()
            
            return decisao
            
        return None
        
    def get_estatisticas(self) -> Dict:
        """Retorna estatísticas das decisões tomadas"""
        return {
            'total_decisoes': len(self.historico_decisoes),
            'propostas_ativas': len(self.propostas_ativas),
            'historico': self.historico_decisoes
        }

# ============================================================================
# SISTEMA DE SIMULAÇÃO
# ============================================================================

class SimulacaoCruzamento:
    """
    Classe principal para executar a simulação do SMA
    """
    
    def __init__(self, num_veiculos: int = 5, tem_emergencia: bool = True):
        # Inicializa componentes
        self.ambiente = CruzamentoEnvironment()
        self.protocolo = ProtocoloNegociacao()
        self.coordenador = CoordenadorAgent()
        
        # Cria veículos
        self.veiculos = []
        direcoes = ['norte', 'sul', 'leste', 'oeste']
        
        for i in range(num_veiculos):
            direcao = random.choice(direcoes)
            # Primeiro veículo é emergência se solicitado
            tipo = 'emergencia' if (i == 0 and tem_emergencia) else 'normal'
            tempo_travessia = 2.0 if tipo == 'emergencia' else 3.0
            
            veiculo = VeiculoAgent(
                agent_id=f'V{i+1}',
                direcao_origem=direcao,
                tipo=tipo,
                tempo_travessia=tempo_travessia
            )
            
            self.veiculos.append(veiculo)
            veiculo.tempo_chegada = i * 0.5
            
            # Adiciona à fila do ambiente
            self.ambiente.adicionar_veiculo_fila(
                veiculo.agent_id,
                direcao,
                tempo_chegada=veiculo.tempo_chegada,
                tipo=tipo
            )
            
        # Estatísticas
        self.estatisticas = {
            'total_atravessias': 0,
            'tempo_medio_espera': 0.0,
            'veiculos_processados': []
        }
        
    def executar_rodada_negociacao(self) -> Optional[str]:
        """
        Executa uma rodada de negociação completa
        """
        print(f"\n{'─'*60}")
        print(f"RODADA DE NEGOCIACAO")
        print(f"{'─'*60}")
        
        # FASE 1: Coleta de Propostas
        print(f"\nFASE 1: Coleta de Propostas")
        propostas_enviadas = 0
        
        for veiculo in self.veiculos:
            if veiculo.estado == 'aguardando':
                estado = veiculo.perceber(self.ambiente)
                proposta = veiculo.criar_proposta(estado)
                self.coordenador.registrar_proposta(proposta)
                propostas_enviadas += 1
        
        if propostas_enviadas == 0:
            print(f"   (Nenhuma proposta recebida)")
            return None
        
        # FASE 2: Coordenador Decide
        print(f"\nFASE 2: Decisao do Coordenador")
        decisao = self.coordenador.coordenar_rodada()
        
        if decisao:
            veiculo_autorizado = decisao['veiculo_autorizado']
            
            # FASE 3: Execução
            print(f"\nFASE 3: Execucao")
            for veiculo in self.veiculos:
                if veiculo.agent_id == veiculo_autorizado:
                    veiculo.permissao_recebida = True
                    veiculo.executar_acao('atravessar', self.ambiente)
                    
                    return veiculo_autorizado
        
        return None
        
    def executar_simulacao(self, max_rodadas: int = 20):
        """
        Executa a simulação completa
        """
        print(f"\n{'='*60}")
        print(f"SIMULACAO DO SISTEMA MULTI-AGENTES")
        print(f"{'='*60}")
        print(f"\nConfiguracao:")
        print(f"   • Total de veiculos: {len(self.veiculos)}")
        
        for v in self.veiculos:
            tipo_str = "EMERGENCIA" if v.tipo == 'emergencia' else "Normal"
            print(f"   [{tipo_str}] {v.agent_id} - Direcao: {v.direcao_origem}")
        
        self.ambiente.mostrar_status()
        
        rodada = 0
        while rodada < max_rodadas:
            # Verifica se todos atravessaram
            if all(v.estado == 'concluido' for v in self.veiculos):
                print(f"\n>> Todos os veiculos atravessaram!")
                break
            
            # Atualiza veículos que estão atravessando
            for veiculo in self.veiculos:
                if veiculo.estado == 'atravessando':
                    acao = veiculo.decidir_acao(self.ambiente)
                    if acao == 'sair_cruzamento':
                        veiculo.executar_acao(acao, self.ambiente)
                        self.estatisticas['total_atravessias'] += 1
                        
                        # Registra estatísticas quando o veículo sai
                        self.estatisticas['veiculos_processados'].append({
                            'id': veiculo.agent_id,
                            'tempo_espera': veiculo.tempo_espera,
                            'tipo': veiculo.tipo
                        })
            
            # Executar negociação se cruzamento está livre
            if not self.ambiente.ocupado:
                veiculo_autorizado = self.executar_rodada_negociacao()
                
                if veiculo_autorizado:
                    # Pequena pausa para visualização
                    time.sleep(0.5)
            
            # Atualiza tempo
            self.ambiente.atualizar_tempo(0.5)
            rodada += 1
            
            # Mostra status periodicamente
            if rodada % 4 == 0:
                self.ambiente.mostrar_status()
            
            time.sleep(0.3)
        
        # IMPORTANTE: Processar veículos que ainda estão atravessando ao final
        for veiculo in self.veiculos:
            if veiculo.estado == 'atravessando':
                # Força a saída do veículo
                veiculo.executar_acao('sair_cruzamento', self.ambiente)
                self.estatisticas['total_atravessias'] += 1
                
                # Registra nas estatísticas
                if not any(v['id'] == veiculo.agent_id for v in self.estatisticas['veiculos_processados']):
                    self.estatisticas['veiculos_processados'].append({
                        'id': veiculo.agent_id,
                        'tempo_espera': veiculo.tempo_espera,
                        'tipo': veiculo.tipo
                    })
        
        self.exibir_resultados()
        
    def exibir_resultados(self):
        """Exibe resultados finais da simulação"""
        print(f"\n{'='*60}")
        print(f"RESULTADOS DA SIMULACAO")
        print(f"{'='*60}")
        
        print(f"\nEstatisticas Gerais:")
        print(f"   • Total de atravessias: {self.estatisticas['total_atravessias']}")
        
        if self.estatisticas['veiculos_processados']:
            tempos = [v['tempo_espera'] for v in self.estatisticas['veiculos_processados']]
            print(f"   • Tempo medio de espera: {sum(tempos)/len(tempos):.2f}s")
            print(f"   • Tempo minimo de espera: {min(tempos):.2f}s")
            print(f"   • Tempo maximo de espera: {max(tempos):.2f}s")
        
        print(f"\nOrdem de Passagem:")
        for i, v in enumerate(self.estatisticas['veiculos_processados'], 1):
            tipo_str = "EMERGENCIA" if v['tipo'] == 'emergencia' else "Normal"
            print(f"   {i}. [{tipo_str}] {v['id']} - Esperou {v['tempo_espera']:.2f}s")
        
        # Estatísticas do coordenador
        stats_coord = self.coordenador.get_estatisticas()
        print(f"\nEstatisticas do Coordenador:")
        print(f"   • Total de decisoes tomadas: {stats_coord['total_decisoes']}")
        
        print(f"\n{'='*60}")

# ============================================================================
# EXPERIMENTOS
# ============================================================================

def executar_experimentos():
    """
    Executa diferentes cenários de teste conforme requisitos do trabalho
    """
    
    print("\n" + "="*60)
    print("EXPERIMENTOS DO TRABALHO")
    print("="*60)
    
    # EXPERIMENTO 1: Cenário Normal
    print("\n\n" + "="*60)
    print("EXPERIMENTO 1: Cenario Normal (5 veiculos)")
    print("="*60)
    sim1 = SimulacaoCruzamento(num_veiculos=5, tem_emergencia=False)
    sim1.executar_simulacao(max_rodadas=30)
    
    time.sleep(2)
    
    # EXPERIMENTO 2: Cenário com Emergência
    print("\n\n" + "="*60)
    print("EXPERIMENTO 2: Cenario com Emergencia (1 emergencia + 4 normais)")
    print("="*60)
    sim2 = SimulacaoCruzamento(num_veiculos=5, tem_emergencia=True)
    sim2.executar_simulacao(max_rodadas=30)
    
    time.sleep(2)
    
    # EXPERIMENTO 3: Tráfego Intenso
    print("\n\n" + "="*60)
    print("EXPERIMENTO 3: Trafego Intenso (1 emergencia + 7 normais)")
    print("="*60)
    sim3 = SimulacaoCruzamento(num_veiculos=8, tem_emergencia=True)
    sim3.executar_simulacao(max_rodadas=40)

# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    # Escolha uma das opções:
    
    # Opção 1: Executar uma simulação simples
    print(">> Executando simulacao simples com negociacao...")
    sim = SimulacaoCruzamento(num_veiculos=5, tem_emergencia=True)
    sim.executar_simulacao(max_rodadas=30)
    
    # Opção 2: Executar todos os experimentos (descomente para usar)
    # print("\n\nExecutar TODOS os experimentos...")
    # time.sleep(2)
    # executar_experimentos()