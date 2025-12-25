from enum import Enum

class ActionType(Enum):
    TRAVERSE = "TRAVERSE"
    EQUIP = "EQUIP"
    UNEQUIP = "UNEQUIP"
    NO_OP = "NO_OP"

class AgentType(Enum):
    ADVERSARIAL = "Adversarial"
    SEMI_COOPERATIVE = "Semi Cooperative"
    FULLY_COOPERATIVE = "Fully Cooperative"

