from enum import Enum

class ActionType(Enum):
    TRAVERSE = "TRAVERSE"
    EQUIP = "EQUIP"
    UNEQUIP = "UNEQUIP"
    NO_OP = "NO_OP"
    TERMINATE = "TERMINATE"

class AgentType(Enum):
    ADVERSARIAL = "Adversarial Agent"
    SEMI_COOPERATIVE = "Semi Cooperative Agent"
    FULLY_COOPERATIVE = "Fully Cooperative Agent"

class GameType(Enum):
    ADVERSARIAL = "Adversarial Game"
    SEMI_COOPERATIVE = "Semi Cooperative Game"
    FULLY_COOPERATIVE = "Fully Cooperative Game"
