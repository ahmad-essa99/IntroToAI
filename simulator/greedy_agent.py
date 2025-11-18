import math
from agent import Agent, AgentType
from enums import ActionType



class GreedyAgent(Agent):
    def __init__(self, id: int, starting_vertex: int):
        super().__init__(id, starting_vertex)
        self._agent_type = AgentType.GREEDY
        self._already_computed_path = []

    def make_move(self, simulator):
        super().make_move(simulator)

        print("hereeee")
        print(self._already_computed_path)

        if (self._already_computed_path and
                self._already_computed_path[-1] in simulator._set_of_targeted_vertices):
            print("Greedy Agent already have a computed path, follow it")

            next_vertex = self._already_computed_path[0]
            self._already_computed_path.pop(0)
            return (ActionType.TRAVERSE, next_vertex)

        print("Run shortest path algo with simple dijkstra")

        graph = simulator._graph
        dist, prev = graph._shortest_path_with_simple_dijkstra(
            self._current_vertex, agent_is_equipped=self._is_equipped)

        best_target = None
        best_dist = math.inf

        for vertex_id in simulator._set_of_targeted_vertices:
            current_vertex_val = dist.get(vertex_id)
            if current_vertex_val < best_dist:
                best_dist = current_vertex_val
                best_target = vertex_id

            elif current_vertex_val == best_dist and current_vertex_val != math.inf and vertex_id < best_target:
                # break tie by lower vertex id
                best_target = vertex_id

        if best_target is None or best_dist == math.inf:
            # there is no reachable target
            return (ActionType.NOOP,)

        path = graph._reconstruct_path(prev, self._current_vertex, best_target)

        if not path:
            return (ActionType.NOOP,)

        print(f"new path computed for Greedy Agent {path}")
        self._already_computed_path = path

        next_vertex = path[0]
        path.pop(0)
        return (ActionType.TRAVERSE, next_vertex)

