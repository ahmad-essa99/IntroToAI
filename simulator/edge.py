class Edge:
    """Undirected weighted edge.

    In PA4, an edge can be *possibly flooded* with an independent probability
    (``flood_prob``). If ``flood_prob`` is None or 0, the edge is treated as
    never-flooded.

    Notes:
        - The *realized* flooded / clear status is sampled per simulation run.
        - The planner operates over belief-states (knowledge about edges).
    """

    def __init__(self, edge_id: int, v1: int, v2: int, weight: float, flood_prob: float | None = None):
        self.id = int(edge_id)
        self.v1 = int(v1)
        self.v2 = int(v2)
        self.weight = float(weight)

        if flood_prob is None:
            self.flood_prob = None
        else:
            p = float(flood_prob)
            self.flood_prob = None if p <= 0.0 else p

    @property
    def is_floodable(self) -> bool:
        return self.flood_prob is not None

    def other(self, v: int) -> int:
        if v == self.v1:
            return self.v2
        if v == self.v2:
            return self.v1
        raise ValueError(f"vertex {v} is not incident to edge {self.id}")

    def key(self) -> tuple[int, int]:
        return (self.v1, self.v2) if self.v1 < self.v2 else (self.v2, self.v1)

    def __repr__(self) -> str:
        fp = "-" if self.flood_prob is None else f"{self.flood_prob:g}"
        return f"Edge(id={self.id}, {self.v1}<->{self.v2}, w={self.weight:g}, flood_prob={fp})"
