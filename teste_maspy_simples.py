# Teste simples para entender o MASPY
from maspy import *

# Testando importação e estrutura básica
print("MASPY importado com sucesso!")
print(f"Versão: {__version__ if '__version__' in dir() else 'desconhecida'}")

# Teste básico de Ambiente
class TestEnv(Environment):
    def acao_teste(self, agt):
        self.print(f"{agt} executou uma ação!")

# Teste básico de Agente
class TestAgent(Agent):
    def __init__(self, nome):
        super().__init__(nome)
        self.add(Belief("teste", "valor"))
        self.add(Goal("objetivo"))

    @pl(gain, Goal("objetivo"))
    def executar(self, src):
        self.print("Plano executado!")
        self.acao_teste()
        self.stop_cycle()

if __name__ == "__main__":
    env = TestEnv()
    agent = TestAgent("AgenteTeste")

    print(f"Nome do agente: {agent.my_name}")

    Admin().connect_to([agent], env)
    Admin().start_system()

    print("\nTeste concluído!")
