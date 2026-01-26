import random
from dataclasses import dataclass
from  graph import Graph


@dataclass
class SampledInstance:
    """A single sampled 'world' for simulation."""

    flooded_edge_ids: set[int]


def sample_instance(graph: Graph, rng: random.Random) -> SampledInstance:
    flooded: set[int] = set()
    for eid in graph.floodable_edge_ids:
        e = graph.edges[eid]
        if rng.random() < float(e.flood_prob):
            flooded.add(eid)
    return SampledInstance(flooded_edge_ids=flooded)

def print_instance(graph: Graph, instance: SampledInstance) -> None:
    print("\n=== Sampled flooding instance ===")
    if not graph.floodable_edge_ids:
        print("(No floodable edges)")
        return
    for idx, eid in enumerate(graph.floodable_edge_ids):
        e = graph.edges[eid]
        status = "FLOODED" if eid in instance.flooded_edge_ids else "CLEAR"
        print(f"fidx={idx:2d} edge#{eid} ({e.v1}-{e.v2}) p={float(e.flood_prob):g} -> {status}")