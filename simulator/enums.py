from enum import Enum

class ActionType(Enum):
    TRAVERSE = "TRAVERSE"
    EQUIP = "EQUIP"
    UNEQUIP = "UNEQUIP"
    NO_OP = "NO_OP"
    TERMINATE = "TERMINATE"

class AgentType(Enum):
    HUMAN = "Human"
    STUPID_GREEDY = "Stupid Greedy"
    THIEF = "Thief"
    GREEDY = "Greedy"
    A_STAR = "A*"
    REAL_TIME_A_STAR = "Real Time A*"