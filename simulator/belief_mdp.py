import itertools
import math
from collections import deque
from dataclasses import dataclass

from edge import Edge
from enums import ActionType, EdgeKnowledge
from graph import Graph
from belief_state import BeliefState

@dataclass
class ActionTransition:
    action: tuple
    cost: float
    next_states: list[tuple[int, float]]  # (next_state_index, prob)


@dataclass
class MDP:
    states: list[BeliefState]
    state_to_idx: dict[BeliefState, int]
    transitions: list[list[ActionTransition]]  # transitions[s] = list of actions
    terminal: list[bool]
    start_distribution: list[tuple[int, float]]
    

def _set_tuple(t: tuple[int, ...], i: int, val: int) -> tuple[int, ...]:
    if t[i] == val:
        return t
    lst = list(t)
    lst[i] = val
    return tuple(lst)


def observe_at_vertex(graph: Graph, v: int, knowledge: tuple[int, ...]) -> list[tuple[tuple[int, ...], float]]:
    """Reveal all UNKNOWN floodable edges incident to vertex v.

    Returns list of (new_knowledge_tuple, probability) over all possible observation outcomes.
    """

    m = len(graph.floodable_edge_ids)
    if m == 0:
        return [(knowledge, 1.0)]
    if not knowledge:
        # Defensive: if caller passed empty, initialize to all UNKNOWN.
        knowledge = (EdgeKnowledge.UNKNOWN,) * m

    unknown_inc: list[int] = []
    for idx in graph.incident_flood_indices(v):
        if knowledge[idx] == EdgeKnowledge.UNKNOWN:
            unknown_inc.append(idx)

    if not unknown_inc:
        return [(knowledge, 1.0)]

    outcomes: list[tuple[tuple[int, ...], float]] = []

    # Each unknown incident edge becomes CLEAR or FLOODED.
    choices = itertools.product([EdgeKnowledge.CLEAR, EdgeKnowledge.FLOODED], repeat=len(unknown_inc))
    for assignment in choices:
        new_k = knowledge
        prob = 1.0
        for idx, status in zip(unknown_inc, assignment, strict=True):
            eid = graph.floodable_edge_ids[idx]
            e: Edge = graph.edges[eid]
            p = float(e.flood_prob)  # must exist for floodable edges
            prob *= p if status == EdgeKnowledge.FLOODED else (1.0 - p)
            new_k = _set_tuple(new_k, idx, status)
        if prob > 0.0:
            outcomes.append((new_k, prob))

    return outcomes


def build_reachable_mdp(
    graph: Graph,
    kits: set[int],
    equip_cost: float,
    unequip_cost: float,
    slow_factor: float,
    start: int,
    target: int,
) -> MDP:
    """Enumerate reachable belief-states and build explicit transitions."""

    m = len(graph.floodable_edge_ids)

    def edge_status_between(knowledge: tuple[int, ...], u: int, v: int) -> int:
        idx = graph.flood_index_between(u, v)
        if idx is None:
            return EdgeKnowledge.CLEAR
        return knowledge[idx]

    # Start: at time 0 we are at start, so we reveal incident edges of start.
    base_knowledge: tuple[int, ...] = (EdgeKnowledge.UNKNOWN,) * m
    start_outcomes = observe_at_vertex(graph, start, base_knowledge)

    # Initial belief distribution over fully observed-at-start states.
    start_distribution: list[tuple[BeliefState, float]] = []
    for k, p in start_outcomes:
        start_distribution.append((BeliefState(start, False, frozenset(kits), k), p))

    # BFS over belief graph (including stochastic observations)
    state_to_idx: dict[BeliefState, int] = {}
    states: list[BeliefState] = []
    q = deque()
    for s, _p in start_distribution:
        if s not in state_to_idx:
            state_to_idx[s] = len(states)
            states.append(s)
            q.append(s)

    def enqueue(bs: BeliefState) -> None:
        if bs not in state_to_idx:
            state_to_idx[bs] = len(states)
            states.append(bs)
            q.append(bs)

    while q:
        bs = q.popleft()
        if bs.v == target:
            continue

        # Equip/unequip
        # Equip consumes the kit at the current vertex.
        if (not bs.equipped) and (bs.v in bs.kit_locations):
            enqueue(BeliefState(bs.v, True, bs.kit_locations - {bs.v}, bs.knowledge))
        if bs.equipped:
            enqueue(BeliefState(bs.v, False, bs.kit_locations | {bs.v}, bs.knowledge))

        # Traverse to neighbors if legal.
        for nxt, e in graph.neighbors(bs.v):
            st = edge_status_between(bs.knowledge, bs.v, nxt)
            if st == EdgeKnowledge.UNKNOWN:
                # In reachable beliefs, incident edges should be observed; defensive skip.
                continue
            if st == EdgeKnowledge.FLOODED and (not bs.equipped):
                continue

            # After arriving at nxt, we observe incident unknown edges of nxt.
            obs = observe_at_vertex(graph, nxt, bs.knowledge)
            for new_k, _prob in obs:
                enqueue(BeliefState(nxt, bs.equipped, bs.kit_locations, new_k))

    # Build transitions table for each state.
    transitions: list[list[ActionTransition]] = [[] for _ in range(len(states))]
    terminal: list[bool] = [False] * len(states)

    for i, bs in enumerate(states):
        if bs.v == target:
            terminal[i] = True
            continue

        # Equip
        if (not bs.equipped) and (bs.v in bs.kit_locations):
            nxt = BeliefState(bs.v, True, bs.kit_locations - {bs.v}, bs.knowledge)
            transitions[i].append(
                ActionTransition(
                    action=(ActionType.EQUIP,),
                    cost=equip_cost,
                    next_states=[(state_to_idx[nxt], 1.0)],
                )
            )

        # Unequip
        if bs.equipped:
            nxt = BeliefState(bs.v, False, bs.kit_locations | {bs.v}, bs.knowledge)
            transitions[i].append(
                ActionTransition(
                    action=(ActionType.UNEQUIP,),
                    cost=unequip_cost,
                    next_states=[(state_to_idx[nxt], 1.0)],
                )
            )

        # Traverse
        for nxt_v, e in graph.neighbors(bs.v):
            st = edge_status_between(bs.knowledge, bs.v, nxt_v)
            if st == EdgeKnowledge.UNKNOWN:
                continue
            if st == EdgeKnowledge.FLOODED and (not bs.equipped):
                continue

            move_cost = e.weight * (slow_factor if bs.equipped else 1.0)
            obs = observe_at_vertex(graph, nxt_v, bs.knowledge)
            nexts: list[tuple[int, float]] = []
            for new_k, prob in obs:
                b2 = BeliefState(nxt_v, bs.equipped, bs.kit_locations, new_k)
                nexts.append((state_to_idx[b2], prob))

            transitions[i].append(
                ActionTransition(
                    action=(ActionType.TRAVERSE, nxt_v),
                    cost=move_cost,
                    next_states=nexts,
                )
            )

    # Convert start distribution to indices
    start_dist_idx: list[tuple[int, float]] = []
    for s, p in start_distribution:
        start_dist_idx.append((state_to_idx[s], p))

    return MDP(
        states=states,
        state_to_idx=state_to_idx,
        transitions=transitions,
        terminal=terminal,
        start_distribution=start_dist_idx,
    )


def value_iteration(
    mdp: MDP,
    eps: float = 1e-9,
    max_iters: int = 20000,
) -> tuple[list[float], list[tuple | None]]:
    """Value iteration for stochastic shortest path (undiscounted, positive costs).

    Practical approach:
    - Initialize V(s)=0 for all states (a lower bound).
    - Repeated Bellman backups increase values toward the optimal expected cost-to-go.
    """

    n = len(mdp.states)
    V: list[float] = [0.0] * n
    policy: list[tuple | None] = [None] * n

    for _it in range(max_iters):
        delta = 0.0

        # Gauss–Seidel style updates (in-place)
        for s in range(n):
            if mdp.terminal[s]:
                V[s] = 0.0
                policy[s] = None
                continue

            best = math.inf
            best_act = None

            for tr in mdp.transitions[s]:
                exp = tr.cost
                for s2, p in tr.next_states:
                    exp += p * V[s2]
                if exp < best:
                    best = exp
                    best_act = tr.action

            # If state has no actions (shouldn't happen for reachable non-terminal states),
            # leave its value as +inf to mark as irregular.
            if best_act is None:
                V[s] = math.inf
                policy[s] = None
                continue

            old = V[s]
            V[s] = best
            policy[s] = best_act
            delta = max(delta, abs(old - best))

        if delta < eps:
            break

    return V, policy


def expected_start_value(mdp: MDP, V: list[float]) -> float:
    """Expected value from the initial start distribution."""
    total = 0.0
    for s, p in mdp.start_distribution:
        total += p * V[s]
    return total