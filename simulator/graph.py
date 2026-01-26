from collections import deque
from dataclasses import dataclass
from edge import Edge


@dataclass
class ParsedProblem:
    n_vertices: int
    edges: list[Edge]
    kits: set[int]
    equip_cost: float
    unequip_cost: float
    slow_factor: float
    start: int
    target: int


class Graph:
    """Undirected weighted graph."""

    def __init__(self, n_vertices: int):
        self.n_vertices = int(n_vertices)
        self.edges: dict[int, Edge] = {}
        self.adj: dict[int, list[int]] = {v: [] for v in range(1, self.n_vertices + 1)}
        # map unordered pair -> edge_id
        self._pair_to_edge_id: dict[tuple[int, int], int] = {}

        # For belief-MDP:
        # floodable edges get a dense index 0..m-1
        self.floodable_edge_ids: list[int] = [] #A list of edge IDs that are floodable
        self._edge_id_to_flood_idx: dict[int, int] = {} # Maps edge_id → flood_index in the belief tuple
        self._pair_to_flood_idx: dict[tuple[int, int], int] = {}  # Maps an undirected vertex pair (min(u,v), max(u,v)) → flood_index
        self._incident_flood_idxs: dict[int, list[int]] = {v: [] for v in range(1, self.n_vertices + 1)} # Maps vertex -> list of floodable edge indices incident to it

    def add_edge(self, e: Edge) -> None:
        if e.id in self.edges:
            raise ValueError(f"duplicate edge id: {e.id}")
        self.edges[e.id] = e
        self.adj[e.v1].append(e.id)
        self.adj[e.v2].append(e.id)

        k = e.key()
        if k in self._pair_to_edge_id:
            raise ValueError(f"duplicate undirected edge between {k[0]} and {k[1]}")
        self._pair_to_edge_id[k] = e.id

        if e.is_floodable:
            idx = len(self.floodable_edge_ids)
            self.floodable_edge_ids.append(e.id)
            self._edge_id_to_flood_idx[e.id] = idx
            self._pair_to_flood_idx[k] = idx
            self._incident_flood_idxs[e.v1].append(idx)
            self._incident_flood_idxs[e.v2].append(idx)

    def neighbors(self, v: int) -> list[tuple[int, Edge]]:
        out: list[tuple[int, Edge]] = []
        for eid in self.adj[v]:
            e = self.edges[eid]
            out.append((e.other(v), e))
        return out

    def edge_between(self, u: int, v: int) -> Edge:
        k = (u, v) if u < v else (v, u)
        eid = self._pair_to_edge_id.get(k)
        if eid is None:
            raise KeyError(f"no edge between {u} and {v}")
        return self.edges[eid]

    def flood_index_between(self, u: int, v: int) -> int | None:
        k = (u, v) if u < v else (v, u)
        return self._pair_to_flood_idx.get(k)

    def incident_flood_indices(self, v: int) -> list[int]:
        return self._incident_flood_idxs.get(v, [])

    def is_reachable_via_sure_edges(self, start: int, goals: set[int]) -> bool:
        """Reachability using only edges with flood_prob==0 (probability 1 unflooded)."""
        q = deque([start])
        seen = {start}
        while q:
            cur = q.popleft()
            if cur in goals:
                return True
            for nxt, e in self.neighbors(cur):
                if e.is_floodable:
                    # floodable => may be flooded with positive prob
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        return False