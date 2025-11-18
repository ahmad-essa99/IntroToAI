from enum import Enum

class ActionType(Enum):
    TRAVERSE = "TRAVERSE"
    EQUIP = "EQUIP"
    UNEQUIP = "UNEQUIP"
    NO_OP = "NO_OP"