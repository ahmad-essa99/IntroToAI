from agent import Agent
from enums import ActionType, AgentType


class HumanAgent(Agent):
    def __init__(self, id: int, starting_vertex: int):
        super().__init__(id, starting_vertex)
        self._agent_type = AgentType.HUMAN

    def make_move(self, simulator):
        super().make_move(simulator)

        if not simulator._set_of_targeted_vertices:
            print(f"{self._agent_type}: no target vertices left -> TERMINATE")
            return (ActionType.TERMINATE,)

        print("Your options:")
        print(" t <vertex>  - traverse to a neighbor (example: t 3)")
        print(" e           - equip amphibian kit")
        print(" u           - unequip amphibian kit")
        print(" n           - do nothing")

        command = input("Enter your next move: ").strip().lower().split()
        cmd = command[0]

        if cmd == "t" and len(command) == 2:
            v = int(command[1])
            return (ActionType.TRAVERSE, v)

        if cmd == "e":
            return (ActionType.EQUIP,)

        if cmd == "u":
            return (ActionType.UNEQUIP,)

        if cmd == "n":
            return (ActionType.NO_OP,)

        print("invalid command -> NO_OP.")
        return (ActionType.NO_OP,)
