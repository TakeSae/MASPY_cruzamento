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
        self.add(Goal("test"))
        print(f"5. Goal added to {name}")

    @pl(gain, Goal("test"))
    def do_test(self, src):
        self.print("6. Plan executing")
        yield self.stop_cycle()

print("7. Agent class OK")

env = TestEnv()
print("8. Env instance OK")

agt = TestAgent("agent1")
print("9. Agent instance OK")

adm = Admin()
print("10. Admin instance OK")

adm.connect_to([agt], env)
print("11. Connected OK")

print("12. Starting system...")
adm.start_system()
print("13. System finished")
