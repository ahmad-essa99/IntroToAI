from enum import Enum

class AgentType(Enum):
    HUMAN = "Human"
    GREEDY = "Stupid Greedy"
    THIEF = "Thief"

class Agent:
    def __init__(self, id: int, starting_vertex: int):

        self._id = id
        self._current_vertex = starting_vertex
        self._num_of_people_picked = 0
        self._num_of_actions = 0
        self._agent_elapsed_time = 0
        self._is_equipped = False
        self._agent_type = None

    def update_current_vertex(self, new_vertex):
        self._current_vertex = new_vertex

    def increase_num_of_actions(self):
        self._num_of_actions+=1

    def increase_elapsed_time(self, step_time):
        self._agent_elapsed_time += step_time

    def make_move(self, simulator):
        self.print_state()
        simulator._graph.print_vertex_info(self._current_vertex)
        print()

    def print_state(self):
        print(f"=== {self._agent_type.value} Agent (ID {self._id}) ===")
        print(f"Current vertex       : {self._current_vertex}")
        print(f"People picked        : {self._num_of_people_picked}")
        print(f"Total actions done   : {self._num_of_actions}")
        print(f"Elapsed time         : {self._agent_elapsed_time}")
        print(f"Equipped with kit?   : {'Yes' if self._is_equipped else 'No'}")
        print("----------------------------")