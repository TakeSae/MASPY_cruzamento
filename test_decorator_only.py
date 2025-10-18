from maspy import *

print("1. Starting")

class TestEnv(Environment):
    pass

print("2. Env defined")

class TestAgent(Agent):
    def __init__(self, name):
        print("3. Init start")
        super().__init__(name)
        print("4. Super done")
        # NOT adding goal here

    @pl(gain, Goal("test"))
    def do_test(self, src):
        print("5. In plan")
        self.stop_cycle()

print("6. Agent defined")

env = TestEnv()
print("7. Env created")

agt = TestAgent("agent1")
print("8. Agent created")

print("9. DONE - NOT starting Admin")
