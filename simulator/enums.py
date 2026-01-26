from enum import Enum, IntEnum

class ActionType(Enum):
    TRAVERSE = "TRAVERSE"
    EQUIP = "EQUIP"
    UNEQUIP = "UNEQUIP"
    NO_OP = "NO_OP"
    TERMINATE = "TERMINATE"
    
class EdgeKnowledge(IntEnum):
    """Per-floodable-edge knowledge in a belief-state."""
    UNKNOWN = 0
    CLEAR = 1
    FLOODED = 2