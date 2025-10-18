from maspy import *

print("1. Import OK")

class TestEnv(Environment):
    pass

print("2. Env class OK")

class TestAgent(Agent):
    def __init__(self, name):
        print(f"3. Creating agent {name}")
        super().__init__(name)
        print(f"4. Agent {name} created")

print("5. Agent class OK")

env = TestEnv()
print("6. Env instance OK")

agt = TestAgent("agent1")
print("7. Agent instance OK")
