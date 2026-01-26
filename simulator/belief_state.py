
from dataclasses import dataclass
from enums import EdgeKnowledge

@dataclass(frozen=True)
class BeliefState:
    """Belief-state for PA4.

    State components:
      - v: current vertex
      - equipped: whether the agent is currently equipped with a kit
      - kit_locations: the vertices where kits are currently available (on the ground)
      - knowledge: per-floodable-edge knowledge (UNKNOWN/CLEAR/FLOODED)

    knowledge is a tuple[int] of length m (m = #floodable edges), where each entry is in:
      {EdgeKnowledge.UNKNOWN, EdgeKnowledge.CLEAR, EdgeKnowledge.FLOODED}.
    """

    v: int
    equipped: bool
    kit_locations: frozenset[int]
    knowledge: tuple[int, ...]

    def __str__(self) -> str:
        if not self.knowledge:
            k = "[]"
        else:
            # Compact: U/C/F per floodable edge index
            mapch = {EdgeKnowledge.UNKNOWN: "U", EdgeKnowledge.CLEAR: "C", EdgeKnowledge.FLOODED: "F"}
            k = "[" + ",".join(mapch.get(x, "?") for x in self.knowledge) + "]"
        kits = "{" + ",".join(str(x) for x in sorted(self.kit_locations)) + "}"
        return f"(v={self.v}, equipped={'1' if self.equipped else '0'}, kits={kits}, K={k})"