import argparse
import random
from belief_mdp import build_reachable_mdp, expected_start_value, value_iteration
from graph import Graph
from parser import parse_input
from belief_state import BeliefState, EdgeKnowledge
from sampling import SampledInstance, sample_instance, print_instance

def build_graph(parsed) -> Graph:
    g = Graph(parsed.n_vertices)
    for e in parsed.edges:
        g.add_edge(e)
    return g


def prompt_vertex(prompt: str, n: int) -> int:
    while True:
        try:
            v = int(input(prompt).strip())
            if 1 <= v <= n:
                return v
        except ValueError:
            pass
        print(f"Please enter an integer in [1, {n}]")
        

def reveal_incident(graph: Graph, instance: SampledInstance, v: int, knowledge: tuple[int, ...]) -> tuple[int, ...]:
    """Reveal all incident UNKNOWN floodable edges at v using the sampled instance."""
    m = len(graph.floodable_edge_ids)
    if m == 0:
        return knowledge
    if not knowledge:
        knowledge = (EdgeKnowledge.UNKNOWN,) * m

    k_list = list(knowledge)
    for idx in graph.incident_flood_indices(v):
        if k_list[idx] != EdgeKnowledge.UNKNOWN:
            continue
        eid = graph.floodable_edge_ids[idx]
        k_list[idx] = EdgeKnowledge.FLOODED if eid in instance.flooded_edge_ids else EdgeKnowledge.CLEAR
    return tuple(k_list)


def print_policy_values(graph: Graph, mdp, V, policy, limit: int | None) -> None:
    print("\n=== Belief-state values and optimal actions (reachable states only) ===")
    shown = 0
    for i, bs in enumerate(mdp.states):
        if limit is not None and shown >= limit:
            print(f"... (stopped after {limit} states)")
            break
        val = V[i]
        act = policy[i]
        tag = "TERMINAL" if mdp.terminal[i] else ""
        if act is None:
            act_str = "(none)"
        elif act[0].name == "TRAVERSE":
            act_str = f"TRAVERSE -> {act[1]}"
        else:
            act_str = act[0].name
        print(f"[{i}] Val={val}  a={act_str}{tag}  state={bs}")

        # Print transitions for this state (all legal actions and their stochastic outcomes)
        if not mdp.terminal[i]:
            print("        transitions:")
            for tr in mdp.transitions[i]:
                a = tr.action
                if a[0].name == "TRAVERSE":
                    a_name = f"TRAVERSE -> {a[1]}"
                else:
                    a_name = a[0].name

                # Format next states as: idx(p=prob)
                nxt_parts = ", ".join(f"{s2}(p={p:.3g})" for s2, p in tr.next_states)
                print(f"          - {a_name:14s} cost={tr.cost:g}  next=[{nxt_parts}]")
        shown += 1


def run_simulation(graph: Graph, parsed, mdp, policy, rng: random.Random) -> None:
    instance = sample_instance(graph, rng)
    print_instance(graph, instance)

    # Start: arrive at start (time 0) => observe incident edges at start.
    v = parsed.start
    equipped = False
    kit_locations = frozenset(parsed.kits)
    m = len(graph.floodable_edge_ids)
    knowledge: tuple[int, ...] = (EdgeKnowledge.UNKNOWN,) * m
    knowledge = reveal_incident(graph, instance, v, knowledge)

    elapsed = 0.0
    steps = 0
    print("\n=== Execution trace ===")
    while True:
        bs = BeliefState(v, equipped, kit_locations, knowledge)
        s_idx = mdp.state_to_idx.get(bs)
        if s_idx is None:
            print(f"Reached an unreachable belief-state: {bs}. Stopping.")
            return

        if v == parsed.target:
            print(f"Arrived at target {v}. Total time: {elapsed:.3f}")
            return

        act = policy[s_idx]
        if act is None:
            print(f"No action available at {bs}. Total time: {elapsed:.3f}")
            return

        steps += 1
        if act[0].name == "EQUIP":
            elapsed += parsed.equip_cost
            equipped = True
            # Consumes the kit at this vertex.
            kit_locations = kit_locations - {v}
            print(f"{steps:3d}) EQUIP at v={v}  (+{parsed.equip_cost})  t={elapsed:.3f}")
        elif act[0].name == "UNEQUIP":
            elapsed += parsed.unequip_cost
            equipped = False
            kit_locations = kit_locations | {v}
            print(f"{steps:3d}) UNEQUIP at v={v}  (+{parsed.unequip_cost})  t={elapsed:.3f}")
        elif act[0].name == "TRAVERSE":
            _, nxt = act
            e = graph.edge_between(v, nxt)
            c = e.weight * (parsed.slow_factor if equipped else 1.0)
            elapsed += c
            print(f"{steps:3d}) TRAVERSE {v}->{nxt} via edge#{e.id} (+{c:g})  t={elapsed:.3f}")
            v = nxt
            knowledge = reveal_incident(graph, instance, v, knowledge)
        else:
            print(f"Unknown action in policy: {act}")
            return

        if steps > 10_000:
            print("Stopping after 10k steps (possible loop).")
            return


def main() -> None:
    ap = argparse.ArgumentParser(description="Belief-state MDP solver for Hurricane Evacuation")
    ap.add_argument("--input", "-i", required=True, help="input file path")
    ap.add_argument("--start", type=int, default=None, help="start vertex (override file)")
    ap.add_argument("--target", type=int, default=None, help="target vertex (override file)")
    ap.add_argument("--sims", type=int, default=2, help="number of simulations to run")
    ap.add_argument("--seed", type=int, default=None, help="random seed")
    ap.add_argument("--print-limit", type=int, default=200, help="max belief-states to print")
    args = ap.parse_args()

    parsed = parse_input(args.input)
    graph = build_graph(parsed)

    # Determine start/target (file, override, or prompt)
    if args.start is not None:
        parsed.start = args.start
    if args.target is not None:
        parsed.target = args.target

    if parsed.start is None:
        parsed.start = prompt_vertex("Start vertex: ", parsed.n_vertices)
    if parsed.target is None:
        parsed.target = prompt_vertex("Target vertex: ", parsed.n_vertices)

    # Illegal scenario check: sure-edge (p=0) reachability to target OR a kit.
    goals = set(parsed.kits)
    goals.add(parsed.target)
    if not graph.is_reachable_via_sure_edges(parsed.start, goals):
        print("illegal scenario: no probability-1 path from start to (target or any kit) using only non-floodable edges")
        return

    kits = set(parsed.kits)

    mdp = build_reachable_mdp(
        graph=graph,
        kits=kits,
        equip_cost=parsed.equip_cost,
        unequip_cost=parsed.unequip_cost,
        slow_factor=parsed.slow_factor,
        start=parsed.start,
        target=parsed.target,
    )

    print(f"Reachable belief-states: {len(mdp.states)}")
    V, policy = value_iteration(mdp)
    print(f"Expected value from start: {expected_start_value(mdp, V):.6f}")

    print_policy_values(graph, mdp, V, policy, limit=args.print_limit)

    rng = random.Random(args.seed)
    for i in range(args.sims):
        print(f"\n\n================ Simulation {i+1} / {args.sims} ================")
        run_simulation(graph, parsed, mdp, policy, rng)


if __name__ == "__main__":
    main()
