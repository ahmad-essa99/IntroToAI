from enum import Enum

class AgentType(Enum):
    HUMAN = "Human"
    GREEDY = "Stupid Greedy"
    THIEF = "Thief"

class Agent:
    def __init__(self, id: int, agent_type: AgentType,
                 starting_vertex: int):

        self._id = id
        self._agent_type = agent_type
        self._current_vertex = starting_vertex
        self._num_of_people_picked = 0
        self._num_of_actions = 0
        self._agent_elapsed_time = 0
        self._is_equipped = False