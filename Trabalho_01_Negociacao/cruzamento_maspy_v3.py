from maspy import *
from enum import Enum
import sys



# SISTEMA DE LOG LEVELS

class LogLevel(Enum):
    SILENT = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

GLOBAL_LOG_LEVEL = LogLevel.INFO



# AMBIENTE - CRUZAMENTO

class CruzamentoEnvironment(Environment):

    def __init__(self):
        super().__init__()
        self.cruzamento_livre = True
        self.veiculos_aguardando = []
        self.veiculo_atravessando = None
        self.historico_travessias = []

    def registrar_chegada(self, agt, veiculo_id, tipo, prioridade):
        self.veiculos_aguardando.append({
            'id': veiculo_id,
            'tipo': tipo,
            'prioridade': prioridade
        })

    def iniciar_travessia(self, agt, veiculo_id):
        if not self.cruzamento_livre:
            self.print(f"AVISO: Cruzamento já ocupado por {self.veiculo_atravessando}")

        self.cruzamento_livre = False
        self.veiculo_atravessando = veiculo_id
        self.historico_travessias.append(veiculo_id)

    def finalizar_travessia(self, agt, veiculo_id):
        self.cruzamento_livre = True
        self.veiculo_atravessando = None

    def get_ordem_travessia(self):
        return self.historico_travessias



# AGENTE VEICULO

class VeiculoAgent(Agent):

    def __init__(self, agt_name=None, tipo="carro", prioridade=10, coordenador="Coordenador", log_level=None):
        super().__init__(agt_name)

        if not tipo or len(tipo.strip()) == 0:
            raise ValueError(f"Tipo de veículo inválido: '{tipo}'")
        if not isinstance(prioridade, (int, float)):
            raise TypeError(f"Prioridade deve ser número, recebido: {type(prioridade)}")
        if prioridade < 0:
            raise ValueError(f"Prioridade não pode ser negativa: {prioridade}")

        self.tipo = tipo
        self.prioridade = prioridade
        self.coordenador = coordenador
        self.log_level = log_level or GLOBAL_LOG_LEVEL
        self.ja_atravessei = False

        self.add(Goal("atravessar"))

    def setup(self):
        pass

    def debug_print(self, msg):
        if self.log_level.value >= LogLevel.DEBUG.value:
            self.print(msg)

    def info_print(self, msg):
        if self.log_level.value >= LogLevel.INFO.value:
            self.print(msg)

    def error_print(self, msg):
        if self.log_level.value >= LogLevel.ERROR.value:
            self.print(msg)

    @pl(gain, Goal("atravessar"))
    def enviar_proposta(self, src):
        # Se já atravessei, não envio mais propostas
        if self.ja_atravessei:
            return

        try:
            try:
                self.call_env_method("registrar_chegada",
                                   self.my_name, self.tipo, self.prioridade)
            except AttributeError:
                self.debug_print("Ambiente não conectado, pulando registro")

            if not isinstance(self.prioridade, (int, float)) or self.prioridade < 0:
                raise ValueError(f"Prioridade inválida: {self.prioridade}")

            proposta = {
                'id': self.my_name,
                'tipo': self.tipo,
                'prio': self.prioridade
            }

            self.debug_print(f"Proposta: tipo={self.tipo}, prio={self.prioridade}")

            coordenador_id = f"{self.coordenador}_1"
            self.send(coordenador_id, tell, Belief("proposta", proposta))

        except ValueError as e:
            self.error_print(f"ERRO ao criar proposta: {e}")
            self.stop_cycle()
        except Exception as e:
            self.error_print(f"ERRO inesperado ao enviar proposta: {type(e).__name__}: {e}")
            self.stop_cycle()

    @pl(gain, Belief("decisao", Any))
    def receber_decisao(self, src, vencedor):
        try:
            if vencedor == self.my_name:
                self.info_print(f">>> VENCI! Atravessando...")
                self.ja_atravessei = True

                try:
                    self.call_env_method("iniciar_travessia", self.my_name)
                except AttributeError:
                    self.debug_print("Ambiente não conectado, pulando notificação")

                # Vencedor para seu ciclo
                self.stop_cycle()
            else:
                # Perdedores não param - continuam participando das próximas rodadas
                self.debug_print(f"Aguardando próxima rodada (Vencedor: {vencedor})")
                # Re-adicionar o goal para enviar proposta na próxima rodada
                self.add(Goal("atravessar"))

        except Exception as e:
            self.error_print(f"ERRO ao processar decisão: {e}")
            self.stop_cycle()



# AGENTE COORDENADOR

class CoordenadorAgent(Agent):

    def __init__(self, agt_name=None, num_veiculos=4, log_level=None):
        super().__init__(agt_name)

        if num_veiculos < 1:
            raise ValueError(f"num_veiculos deve ser >= 1, recebido: {num_veiculos}")

        self.num_veiculos = num_veiculos
        self.contador_propostas = 0
        self.log_level = log_level or GLOBAL_LOG_LEVEL
        self.veiculos_que_atravessaram = []
        self.rodada_atual = 1

    def debug_print(self, msg):
        if self.log_level.value >= LogLevel.DEBUG.value:
            self.print(msg)

    def info_print(self, msg):
        if self.log_level.value >= LogLevel.INFO.value:
            self.print(msg)

    def error_print(self, msg):
        if self.log_level.value >= LogLevel.ERROR.value:
            self.print(msg)

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

            # Calcular quantos veículos ainda precisam atravessar
            veiculos_restantes = self.num_veiculos - len(self.veiculos_que_atravessaram)

            if self.contador_propostas >= veiculos_restantes:
                self.debug_print(f"Todas as {veiculos_restantes} propostas recebidas. Decidindo...")
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
                # Adicionar goal para próxima decisão quando recebermos propostas suficientes
                self.debug_print(f"Preparando rodada {self.rodada_atual}...")
            else:
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

if __name__ == "__main__":
    try:
        print("="*70)
        print("SISTEMA MULTI-AGENTES DE NEGOCIACAO EM CRUZAMENTO v3.0")
        print("Trabalho 1 - SMA 2025.2 - UTFPR")
        print("="*70)

        print("\nConfiguracao do Sistema:")
        print("  - 1 Coordenador")
        print("  - 4 Veiculos")
        print(f"  - Log Level: {GLOBAL_LOG_LEVEL.name}")
        print("\n  Veiculos:")
        print("    - Veiculo1: carro (prioridade=10)")
        print("    - Veiculo2: ambulancia (prioridade=100) [EMERGENCIA]")
        print("    - Veiculo3: onibus (prioridade=30)")
        print("    - Veiculo4: moto (prioridade=5)")

        print("\n  Protocolo de Negociacao:")
        print("    1. Veiculos registram chegada no ambiente")
        print("    2. Veiculos enviam propostas ao Coordenador")
        print("    3. Coordenador coleta todas as propostas")
        print("    4. Coordenador avalia e decide por maior prioridade")
        print("    5. Coordenador notifica todos os veiculos (broadcast)")
        print("    6. Vencedor notifica ambiente e 'atravessa'")
        print("    7. Todos os agentes param seus ciclos\n")

        print("="*70 + "\n")

        NUM_VEICULOS = 4
        if NUM_VEICULOS < 2:
            raise ValueError("Sistema requer pelo menos 2 veículos")

        coord = CoordenadorAgent("Coordenador",
                                num_veiculos=NUM_VEICULOS,
                                log_level=GLOBAL_LOG_LEVEL)

        v1 = VeiculoAgent("Veiculo1",
                         tipo="carro",
                         prioridade=10,
                         log_level=GLOBAL_LOG_LEVEL)

        v2 = VeiculoAgent("Veiculo2",
                         tipo="ambulancia",
                         prioridade=100,
                         log_level=GLOBAL_LOG_LEVEL)

        v3 = VeiculoAgent("Veiculo3",
                         tipo="onibus",
                         prioridade=30,
                         log_level=GLOBAL_LOG_LEVEL)

        v4 = VeiculoAgent("Veiculo4",
                         tipo="moto",
                         prioridade=5,
                         log_level=GLOBAL_LOG_LEVEL)


        agentes = [coord, v1, v2, v3, v4]
        if None in agentes:
            raise RuntimeError("Falha ao criar um ou mais agentes")

        env = CruzamentoEnvironment()

        Admin().connect_to(agentes, env)

        Admin().start_system()

        print("\n" + "="*70)
        print("SISTEMA ENCERRADO COM SUCESSO")
        print("="*70)

#TODO: melhorar as mensagens de erro quando possível
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
