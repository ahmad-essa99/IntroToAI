from agent import Agent
from enums import ActionType, AgentType
import math


class ThiefAgent(Agent):
    def __init__(self, id: int, starting_vertex: int):
        super().__init__(id, starting_vertex)
        self._agent_type = AgentType.THIEF

    def make_move(self, simulator):
        super().make_move(simulator)

        if not any(simulator._active_agents.values()):
            print("ThiefAgent: there is no other active agents -> TERMINATE")
            return (ActionType.TERMINATE,)

        if sum(simulator._kits_locations.values()) < 1:
            print("ThiefAgent: no kits left but other agents still active -> NO_OP")
            return (ActionType.NO_OP,)

        if not self._is_equipped:
            return self._move_towards_kit(simulator)
        else:
            return self._run_away(simulator)

    def _move_towards_kit(self, simulator):
        graph = simulator._graph

        if simulator._kits_locations.get(self._current_vertex, 0) > 0:
            print("ThiefAgent: kit on current vertex -> EQUIP")
            return (ActionType.EQUIP,)

        dist, prev = graph._shortest_path_with_simple_dijkstra(
            source_vertex=self._current_vertex,
            agent_is_equipped=False
        )

        best_vertex = None
        best_dist = math.inf

        for v, num_kits in simulator._kits_locations.items():
            if num_kits <= 0:
                continue
            d = dist.get(v, math.inf)
            if d < best_dist:
                best_dist = d
                best_vertex = v
            elif d == best_dist and d != math.inf and best_vertex is not None and v < best_vertex:
                best_vertex = v

        if best_vertex is None or best_dist == math.inf:
            assert True, "ThiefAgent: _move_towards_kit, should never happen 1"

        path = graph._reconstruct_path(prev, self._current_vertex, best_vertex)
        if not path:
            assert True, "ThiefAgent: _move_towards_kit, should never happen 2"

        next_vertex = path[0]
        print(f"ThiefAgent: moving towards kit at {best_vertex} via {next_vertex}")
        return (ActionType.TRAVERSE, next_vertex)


    def _run_away(self, simulator):
        graph = simulator._graph

        other_agents_positions = [
            a._current_vertex
            for a in simulator._agents
            if a is not self and simulator._active_agents.get(a._id)
        ]

        if not other_agents_positions:
            assert True, "ThiefAgent: _run_away, should never happen 1"

        neighbor_vertices = graph.expand(self._current_vertex, is_equipped=True)

        if not neighbor_vertices:
            print("ThiefAgent: no neighbors to run to -> TERMINATE")
            return (ActionType.TERMINATE,)

        dists_from_others = []
        for pos in other_agents_positions:
            dist_from_pos, _ = graph._shortest_path_with_simple_dijkstra(
                source_vertex=pos,
                agent_is_equipped=True
            )
            dists_from_others.append(dist_from_pos)

        best_neighbor = None
        best_score = -math.inf
        best_edge_id = None  # for tie-breaking on edges

        for v in neighbor_vertices:
            # For each neighbor, compute min distance to any other agent
            min_d = math.inf
            for dist in dists_from_others:
                d = dist.get(v, math.inf)
                if d < min_d:
                    min_d = d

            score = min_d  # we want to maximize this

            edge_id = graph.get_edge(self._current_vertex, v)._id
            if score > best_score:
                best_score = score
                best_neighbor = v
                best_edge_id = edge_id
            elif score == best_score:
                # tie break: lowest vertex id, then lowest edge id
                if best_neighbor is None or v < best_neighbor or (v == best_neighbor and edge_id < best_edge_id):
                    best_neighbor = v
                    best_edge_id = edge_id

        if best_neighbor is None:
            print("ThiefAgent: no good neighbor to run to -> NO_OP")
            return (ActionType.NO_OP,)

        print(f"ThiefAgent: running away to vertex {best_neighbor} (score={best_score})")
        return (ActionType.TRAVERSE, best_neighbor)
