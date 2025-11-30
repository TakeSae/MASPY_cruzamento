from maspy import *
from gui.start import start_interface
from enum import Enum
from dataclasses import dataclass
import argparse
import sys



# SISTEMA DE LOG LEVELS

class LogLevel(Enum):
    SILENT = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

GLOBAL_LOG_LEVEL = LogLevel.INFO



# DATACLASS PARA PROPOSTAS

@dataclass
class Proposta:
    id: str
    tipo: str
    prio: float

    def to_dict(self):
        return {'id': self.id, 'tipo': self.tipo, 'prio': self.prio}

    @staticmethod
    def from_dict(data: dict) -> 'Proposta':
        return Proposta(id=data['id'], tipo=data['tipo'], prio=data['prio'])



# CONFIGURAÇÃO DOS VEÍCULOS

VEICULOS_CONFIG = [
    {"nome": "Veiculo1", "tipo": "carro", "prioridade": 10},
    {"nome": "Veiculo2", "tipo": "ambulancia", "prioridade": 100},
    {"nome": "Veiculo3", "tipo": "onibus", "prioridade": 30},
    {"nome": "Veiculo4", "tipo": "moto", "prioridade": 5},
]

# CONFIGURAÇÕES DE EXPERIMENTOS

EXPERIMENTOS = {
    "padrao": {
        "titulo": "Cenário Padrão",
        "descricao": "4 veículos com prioridades diferentes",
        "veiculos": VEICULOS_CONFIG
    },
    "base": {
        "titulo": "Cenário Base",
        "descricao": "Ambulância deve vencer contra veículos normais",
        "veiculos": [
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 30},
        ]
    },
    "emergencias": {
        "titulo": "Múltiplas Emergências",
        "descricao": "Ambulância1 (prio=100) deve vencer entre emergências",
        "veiculos": [
            {"nome": "Ambulancia1", "tipo": "ambulancia", "prioridade": 100},
            {"nome": "Ambulancia2", "tipo": "ambulancia", "prioridade": 95},
            {"nome": "Bombeiros", "tipo": "bombeiros", "prioridade": 98},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
        ]
    },
    "iguais": {
        "titulo": "Prioridades Iguais",
        "descricao": "Todos com mesma prioridade - ordem de processamento",
        "veiculos": [
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro2", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro3", "tipo": "carro", "prioridade": 10},
            {"nome": "Carro4", "tipo": "carro", "prioridade": 10},
        ]
    },
    "pesados": {
        "titulo": "Cargas Pesadas",
        "descricao": "Caminhão (prio=50) deve vencer",
        "veiculos": [
            {"nome": "Caminhao1", "tipo": "caminhao", "prioridade": 50},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 40},
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 10},
        ]
    },
    "misto": {
        "titulo": "Cenário Misto (6 veículos)",
        "descricao": "Ambulância deve vencer entre 6 veículos diferentes",
        "veiculos": [
            {"nome": "Moto1", "tipo": "moto", "prioridade": 5},
            {"nome": "Carro1", "tipo": "carro", "prioridade": 15},
            {"nome": "Onibus1", "tipo": "onibus", "prioridade": 35},
            {"nome": "Caminhao1", "tipo": "caminhao", "prioridade": 45},
            {"nome": "Taxi1", "tipo": "taxi", "prioridade": 20},
            {"nome": "Ambulancia", "tipo": "ambulancia", "prioridade": 100},
        ]
    },
    "estresse": {
        "titulo": "Teste de Estresse (10 veículos)",
        "descricao": "Veículo10 (prio=100) deve vencer entre 10 veículos",
        "veiculos": [
            {"nome": "Veiculo1", "tipo": "veiculo", "prioridade": 10},
            {"nome": "Veiculo2", "tipo": "veiculo", "prioridade": 20},
            {"nome": "Veiculo3", "tipo": "veiculo", "prioridade": 30},
            {"nome": "Veiculo4", "tipo": "veiculo", "prioridade": 40},
            {"nome": "Veiculo5", "tipo": "veiculo", "prioridade": 50},
            {"nome": "Veiculo6", "tipo": "veiculo", "prioridade": 60},
            {"nome": "Veiculo7", "tipo": "veiculo", "prioridade": 70},
            {"nome": "Veiculo8", "tipo": "veiculo", "prioridade": 80},
            {"nome": "Veiculo9", "tipo": "veiculo", "prioridade": 90},
            {"nome": "Veiculo10", "tipo": "veiculo", "prioridade": 100},
        ]
    },
}



# CLASSE BASE COM LOGGING

class LoggableAgent(Agent):

    def __init__(self, agt_name=None, log_level=None):
        super().__init__(agt_name)
        self.log_level = log_level or GLOBAL_LOG_LEVEL

    def debug_print(self, msg):
        if self.log_level.value >= LogLevel.DEBUG.value:
            self.print(msg)

    def info_print(self, msg):
        if self.log_level.value >= LogLevel.INFO.value:
            self.print(msg)

    def error_print(self, msg):
        if self.log_level.value >= LogLevel.ERROR.value:
            self.print(msg)

    def has_environment(self):
        """Verifica se o agente está conectado a um ambiente."""
        try:
            return hasattr(self, '_env') and self._env is not None
        except:
            return False

    def safe_env_call(self, method_name, *args):
        """Chama método do ambiente de forma segura."""
        try:
            self.call_env_method(method_name, *args)
            return True
        except (AttributeError, Exception) as e:
            self.debug_print(f"Ambiente não disponível para {method_name}: {e}")
            return False



# AMBIENTE - CRUZAMENTO

class CruzamentoEnvironment(Environment):

    def __init__(self):
        super().__init__()

        # Criar Percepts observáveis para a GUI
        self.create(Percept("sistema_status", "inicializando"))
        self.create(Percept("cruzamento_livre", "sim"))
        self.create(Percept("veiculos_aguardando", 0))
        self.create(Percept("veiculo_atravessando", "nenhum"))
        self.create(Percept("rodada_atual", 0))

        # Estado interno
        self.cruzamento_livre = True
        self.veiculos_aguardando_list = []
        self.veiculo_atravessando = None
        self.historico_travessias = []

    def registrar_chegada(self, agt, veiculo_id, tipo, prioridade):
        self.veiculos_aguardando_list.append({
            'id': veiculo_id,
            'tipo': tipo,
            'prioridade': prioridade
        })

        # Atualizar Percepts para GUI
        self.change(Percept("veiculos_aguardando", Any), len(self.veiculos_aguardando_list))
        self.change(Percept("sistema_status", Any), "aguardando_propostas")

    def iniciar_travessia(self, agt, veiculo_id):
        if not self.cruzamento_livre:
            self.print(f"AVISO: Cruzamento já ocupado por {self.veiculo_atravessando}")

        self.cruzamento_livre = False
        self.veiculo_atravessando = veiculo_id
        self.historico_travessias.append(veiculo_id)

        # Atualizar Percepts para GUI
        self.change(Percept("cruzamento_livre", Any), "nao")
        self.change(Percept("veiculo_atravessando", Any), veiculo_id)
        self.change(Percept("rodada_atual", Any), len(self.historico_travessias))

    def finalizar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = True
        self.veiculo_atravessando = None

        # Atualizar Percepts para GUI
        self.change(Percept("cruzamento_livre", Any), "sim")
        self.change(Percept("veiculo_atravessando", Any), "nenhum")

    def get_ordem_travessia(self):
        return self.historico_travessias



# AGENTE VEICULO

class VeiculoAgent(LoggableAgent):

    def __init__(self, agt_name=None, tipo="carro", prioridade=10, coordenador="Coordenador", log_level=None):
        super().__init__(agt_name, log_level)

        if not tipo or len(tipo.strip()) == 0:
            raise ValueError(f"Tipo de veículo inválido: '{tipo}'")
        if not isinstance(prioridade, (int, float)):
            raise TypeError(f"Prioridade deve ser número, recebido: {type(prioridade)}")
        if prioridade < 0:
            raise ValueError(f"Prioridade não pode ser negativa: {prioridade}")

        # Adicionar Beliefs observáveis para GUI
        self.add(Belief("tipo", tipo))
        self.add(Belief("prioridade", prioridade))
        self.add(Belief("status", "aguardando"))
        self.add(Belief("atravessou", "nao"))

        self.tipo = tipo
        self.prioridade = prioridade
        self.coordenador = coordenador
        self.ja_atravessei = False

        self.add(Goal("atravessar"))

    def setup(self):
        pass

    def _update_status(self, new_status):
        """Atualiza o status observável do agente."""
        old_belief = self.get(Belief("status", Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief("status", new_status))

    @pl(gain, Goal("atravessar"))
    def enviar_proposta(self, src):
        # Se já atravessei, não envio mais propostas
        if self.ja_atravessei:
            return

        try:
            self._update_status("enviando_proposta")

            self.safe_env_call("registrar_chegada", self.my_name, self.tipo, self.prioridade)

            if not isinstance(self.prioridade, (int, float)) or self.prioridade < 0:
                raise ValueError(f"Prioridade inválida: {self.prioridade}")

            proposta = Proposta(id=self.my_name, tipo=self.tipo, prio=self.prioridade)

            self.debug_print(f"Proposta: tipo={self.tipo}, prio={self.prioridade}")

            coordenador_id = f"{self.coordenador}_1"
            self.send(coordenador_id, tell, Belief("proposta", proposta.to_dict()))

            self._update_status("proposta_enviada")

        except ValueError as e:
            self._update_status("erro")
            self.error_print(f"ERRO ao criar proposta: {e}")
            self.stop_cycle()
        except Exception as e:
            self._update_status("erro")
            self.error_print(f"ERRO inesperado ao enviar proposta: {type(e).__name__}: {e}")
            self.stop_cycle()

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        try:
            if vencedor == self.my_name:
                self.info_print(f">>> VENCI! Atravessando...")
                self.ja_atravessei = True

                # Atualizar Beliefs observáveis
                self._update_status("atravessando")
                old_atravessou = self.get(Belief("atravessou", Any))
                if old_atravessou:
                    self.rm(old_atravessou)
                self.add(Belief("atravessou", "sim"))

                self.safe_env_call("iniciar_travessia", self.my_name)

                self._update_status("concluido")
                # Vencedor para seu ciclo
                self.stop_cycle()
            else:
                # Perdedores não param - continuam participando das próximas rodadas
                self._update_status("aguardando_proxima_rodada")
                self.debug_print(f"Aguardando próxima rodada (Vencedor: {vencedor})")
                # Re-adicionar o goal para enviar proposta na próxima rodada
                self.add(Goal("atravessar"))

        except Exception as e:
            self._update_status("erro")
            self.error_print(f"ERRO ao processar decisão: {e}")
            self.stop_cycle()



# AGENTE COORDENADOR

class CoordenadorAgent(LoggableAgent):

    def __init__(self, agt_name=None, num_veiculos=4, log_level=None):
        super().__init__(agt_name, log_level)

        if num_veiculos < 1:
            raise ValueError(f"num_veiculos deve ser >= 1, recebido: {num_veiculos}")

        # Adicionar Beliefs observáveis para GUI
        self.add(Belief("rodada_atual", 1))
        self.add(Belief("propostas_recebidas", 0))
        self.add(Belief("status", "aguardando_propostas"))
        self.add(Belief("vencedor_atual", "nenhum"))
        self.add(Belief("total_veiculos", num_veiculos))
        self.add(Belief("veiculos_processados", 0))

        self.num_veiculos = num_veiculos
        self.contador_propostas = 0
        self.veiculos_que_atravessaram = []
        self.rodada_atual = 1

    def _update_status(self, new_status):
        """Atualiza o status observável do coordenador."""
        old_belief = self.get(Belief("status", Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief("status", new_status))

    def _update_belief(self, name, value):
        """Atualiza um Belief observável."""
        old_belief = self.get(Belief(name, Any))
        if old_belief:
            self.rm(old_belief)
        self.add(Belief(name, value))

    @pl(gain, Belief("proposta", Any))
    def coletar_propostas(self, src, dados):
        try:
            if not isinstance(dados, dict):
                raise TypeError(f"Proposta deve ser dict, recebido: {type(dados)}")

            required_fields = ['id', 'tipo', 'prio']
            for field in required_fields:
                if field not in dados:
                    raise KeyError(f"Campo obrigatório '{field}' faltando na proposta")

            # Ignorar propostas de veículos que já atravessaram
            if dados['id'] in self.veiculos_que_atravessaram:
                self.debug_print(f"Proposta ignorada de {dados['id']} (já atravessou)")
                return

            self.debug_print(f"Recebi de {src}: tipo={dados['tipo']}, prio={dados['prio']}")
            self.contador_propostas += 1

            # Atualizar Belief observável
            self._update_belief("propostas_recebidas", self.contador_propostas)

            # Calcular quantos veículos ainda precisam atravessar
            veiculos_restantes = self.num_veiculos - len(self.veiculos_que_atravessaram)

            if self.contador_propostas >= veiculos_restantes:
                self.debug_print(f"Todas as {veiculos_restantes} propostas recebidas. Decidindo...")
                self._update_status("avaliando_propostas")
                self.add(Goal("decidir"))

        except (TypeError, KeyError) as e:
            self.error_print(f"ERRO ao coletar proposta de {src}: {e}")
        except Exception as e:
            self.error_print(f"ERRO inesperado ao coletar proposta: {type(e).__name__}: {e}")

    @pl(gain, Goal("decidir"))
    def decidir_vencedor(self, src):
        try:
            self.info_print("\n" + "="*50)
            self.info_print(f"RODADA {self.rodada_atual} - AVALIANDO PROPOSTAS")
            self.info_print("="*50)

            propostas = self.get(Belief("proposta", Any), all=True, ck_src=False)

            if not propostas:
                raise ValueError("Nenhuma proposta recebida do sistema")

            if len(propostas) == 0:
                raise ValueError("Lista de propostas vazia")

            # Filtrar propostas de veículos que já atravessaram
            propostas_validas = []
            self.debug_print(f"Veículos que já atravessaram: {self.veiculos_que_atravessaram}")

            for prop in propostas:
                try:
                    # Acessar dados da proposta - MASPY usa .values, não .args
                    dados = prop.values

                    self.debug_print(f"Verificando proposta de {dados['id']}")

                    if dados['id'] not in self.veiculos_que_atravessaram:
                        propostas_validas.append(prop)
                        self.debug_print(f"  -> Proposta válida!")
                    else:
                        self.debug_print(f"  -> Já atravessou, ignorando")

                except Exception as e:
                    self.error_print(f"ERRO ao acessar proposta: {e}, tipo: {type(prop)}")
                    import traceback
                    traceback.print_exc()
                    continue

            if len(propostas_validas) == 0:
                self.info_print("Todos os veículos já atravessaram!")
                self.stop_cycle()
                return

            self.info_print(f"\nTotal: {len(propostas_validas)} propostas válidas (de {len(propostas)} recebidas)")

            melhor_prioridade = -1
            vencedor_id = None
            vencedor_dados = None

            for i, prop in enumerate(propostas_validas):
                try:
                    dados = prop.values

                    if 'id' not in dados or 'tipo' not in dados or 'prio' not in dados:
                        raise KeyError(f"Proposta {i} com campos faltando: {dados}")

                    if not isinstance(dados['prio'], (int, float)):
                        raise TypeError(f"Prioridade inválida em {dados['id']}: {dados['prio']}")

                    if dados['prio'] < 0:
                        raise ValueError(f"Prioridade negativa em {dados['id']}: {dados['prio']}")

                    self.debug_print(f"  - {dados['id']}: {dados['tipo']} (prio={dados['prio']})")

                    if dados['prio'] > melhor_prioridade:
                        melhor_prioridade = dados['prio']
                        vencedor_id = dados['id']
                        vencedor_dados = dados

                except (KeyError, TypeError, ValueError) as e:
                    self.error_print(f"ERRO ao processar proposta {i}: {e}")
                    continue

            if vencedor_id is None:
                raise RuntimeError("Nenhum vencedor válido encontrado após avaliar propostas")

            self.veiculos_que_atravessaram.append(vencedor_id)

            # Atualizar Beliefs observáveis
            self._update_belief("vencedor_atual", vencedor_id)
            self._update_belief("veiculos_processados", len(self.veiculos_que_atravessaram))

            self.info_print("\n" + "="*50)
            self.info_print(f">>> VENCEDOR RODADA {self.rodada_atual}: {vencedor_dados['id']}")
            self.info_print(f"  Tipo: {vencedor_dados['tipo']}")
            self.info_print(f"  Prioridade: {vencedor_dados['prio']}")
            self.info_print("="*50 + "\n")

            self.send(broadcast, tell, Belief("decisao", vencedor_id))

            # Preparar próxima rodada se ainda houver veículos
            if len(self.veiculos_que_atravessaram) < self.num_veiculos:
                self.rodada_atual += 1
                self.contador_propostas = 0

                # Atualizar Beliefs observáveis para próxima rodada
                self._update_belief("rodada_atual", self.rodada_atual)
                self._update_belief("propostas_recebidas", 0)
                self._update_status("aguardando_propostas")

                self.debug_print(f"Preparando rodada {self.rodada_atual}...")
            else:
                self._update_status("concluido")

                self.info_print("\n" + "="*50)
                self.info_print("TODAS AS RODADAS CONCLUÍDAS!")
                self.info_print(f"Ordem de travessia: {' -> '.join(self.veiculos_que_atravessaram)}")
                self.info_print("="*50 + "\n")
                self.stop_cycle()

        except ValueError as e:
            self.error_print(f"ERRO DE VALIDAÇÃO: {e}")
            self.error_print("Sistema não pode decidir vencedor. Encerrando.")
            self.stop_cycle()

        except RuntimeError as e:
            self.error_print(f"ERRO DE EXECUÇÃO: {e}")
            self.error_print("Falha crítica no protocolo de negociação.")
            self.stop_cycle()

        except Exception as e:
            self.error_print(f"ERRO INESPERADO: {type(e).__name__}: {e}")
            self.error_print("Sistema encerrando devido a erro não tratado.")
            self.stop_cycle()



# EXECUCAO PRINCIPAL

def parse_arguments():
    """Parse argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Sistema Multi-Agentes de Negociação em Cruzamento"
    )
    parser.add_argument(
        '--gui',
        action='store_true',
        default=True,
        help='Iniciar com interface gráfica (padrão: True)'
    )
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Executar sem interface gráfica'
    )
    parser.add_argument(
        '--log-level',
        choices=['SILENT', 'ERROR', 'INFO', 'DEBUG'],
        default='INFO',
        help='Nível de log (padrão: INFO)'
    )
    parser.add_argument(
        '--experimento',
        choices=list(EXPERIMENTOS.keys()),
        default=None,
        help=f'Experimento a executar: {", ".join(EXPERIMENTOS.keys())}'
    )
    parser.add_argument(
        '--listar',
        action='store_true',
        help='Listar experimentos disponíveis'
    )
    return parser.parse_args()


def listar_experimentos():
    """Lista todos os experimentos disponíveis."""
    print("\n" + "="*70)
    print("EXPERIMENTOS DISPONÍVEIS")
    print("="*70 + "\n")

    for key, exp in EXPERIMENTOS.items():
        print(f"  {key}:")
        print(f"    Título: {exp['titulo']}")
        print(f"    Descrição: {exp['descricao']}")
        print(f"    Veículos: {len(exp['veiculos'])}")
        print()

    print("Uso: python cruzamento_maspy_gui.py --experimento <nome>")
    print("="*70 + "\n")


def menu_interativo():
    """Menu interativo para escolher experimento."""
    print("\n" + "="*70)
    print("SELECIONE UM EXPERIMENTO")
    print("="*70 + "\n")

    opcoes = list(EXPERIMENTOS.keys())
    for i, key in enumerate(opcoes, 1):
        exp = EXPERIMENTOS[key]
        print(f"  {i}. {exp['titulo']} ({len(exp['veiculos'])} veículos)")

    print(f"\n  0. Sair")
    print()

    while True:
        try:
            escolha = input("Escolha (número): ").strip()
            if escolha == "0":
                return None

            idx = int(escolha) - 1
            if 0 <= idx < len(opcoes):
                return opcoes[idx]
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            print("Digite um número válido.")
        except KeyboardInterrupt:
            return None


def criar_veiculos(config, log_level):
    """Cria veículos a partir da configuração."""
    veiculos = []
    for veiculo_config in config:
        veiculo = VeiculoAgent(
            veiculo_config["nome"],
            tipo=veiculo_config["tipo"],
            prioridade=veiculo_config["prioridade"],
            log_level=log_level
        )
        veiculos.append(veiculo)
    return veiculos


def imprimir_configuracao(config, log_level):
    """Imprime a configuração do sistema."""
    print("="*70)
    print("SISTEMA MULTI-AGENTES DE NEGOCIACAO EM CRUZAMENTO v4.0")
    print("Trabalho 1 - SMA 2025.2 - UTFPR")
    print("="*70)

    print("\nConfiguracao do Sistema:")
    print("  - 1 Coordenador")
    print(f"  - {len(config)} Veiculos")
    print(f"  - Log Level: {log_level.name}")
    print("\n  Veiculos:")
    for v in config:
        emergencia = " [EMERGENCIA]" if v["prioridade"] >= 100 else ""
        print(f"    - {v['nome']}: {v['tipo']} (prioridade={v['prioridade']}){emergencia}")

    print("\n  Protocolo de Negociacao:")
    print("    1. Veiculos registram chegada no ambiente")
    print("    2. Veiculos enviam propostas ao Coordenador")
    print("    3. Coordenador coleta todas as propostas")
    print("    4. Coordenador avalia e decide por maior prioridade")
    print("    5. Coordenador notifica todos os veiculos (broadcast)")
    print("    6. Vencedor notifica ambiente e 'atravessa'")
    print("    7. Processo repete até todos atravessarem\n")

    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        args = parse_arguments()

        # Listar experimentos se solicitado
        if args.listar:
            listar_experimentos()
            sys.exit(0)

        # Configurar log level
        log_level = LogLevel[args.log_level]

        # Escolher experimento
        if args.experimento:
            experimento_key = args.experimento
        else:
            # Menu interativo se não especificado
            experimento_key = menu_interativo()
            if experimento_key is None:
                print("\nSaindo...")
                sys.exit(0)

        # Obter configuração do experimento
        experimento = EXPERIMENTOS[experimento_key]
        veiculos_config = experimento["veiculos"]

        print(f"\n>>> Experimento selecionado: {experimento['titulo']}")
        print(f"    {experimento['descricao']}\n")

        # Imprimir configuração
        imprimir_configuracao(veiculos_config, log_level)

        NUM_VEICULOS = len(veiculos_config)
        if NUM_VEICULOS < 2:
            raise ValueError("Sistema requer pelo menos 2 veículos")

        # Inicializar Admin com logging para GUI
        Admin(listener_log=True)

        # Criar coordenador
        coord = CoordenadorAgent("Coordenador",
                                num_veiculos=NUM_VEICULOS,
                                log_level=log_level)

        # Criar veículos a partir da configuração
        veiculos = criar_veiculos(veiculos_config, log_level)

        agentes = [coord] + veiculos
        if None in agentes:
            raise RuntimeError("Falha ao criar um ou mais agentes")

        env = CruzamentoEnvironment()

        Admin().connect_to(agentes, env)

        # Iniciar sistema
        if args.no_gui:
            Admin().start_system()
        else:
            start_interface()

        print("\n" + "="*70)
        print("SISTEMA ENCERRADO COM SUCESSO")
        print("="*70)

    except ValueError as e:
        print(f"\n[ERRO DE CONFIGURAÇÃO] {e}")
        sys.exit(1)

    except RuntimeError as e:
        print(f"\n[ERRO DE EXECUÇÃO] {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n[INTERROMPIDO PELO USUÁRIO]")
        print("Sistema sendo encerrado...")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] {type(e).__name__}: {e}")
        print("Sistema não pode continuar.")
        import traceback
        traceback.print_exc()
        sys.exit(1)
