from __future__ import annotations
from enums import ActionType
from graph import Graph

class State:

    def __init__(self, current_vertex: int, is_equipped: bool, targeted_vertices,
                 kits_locations:dict, graph: Graph):
        self._current_vertex = current_vertex
        self._is_equipped = is_equipped
        self._targeted_vertices = targeted_vertices
        self._kits_locations = kits_locations
        self._graph = graph


    def expand(self)-> list[State]:
        expand_state_list = []
        expand_vertices_list = self._graph.expand(self._current_vertex, self._is_equipped)
        for vertex_id in expand_vertices_list:
            new_targeted_vertices = list(self._targeted_vertices)
            if vertex_id in new_targeted_vertices:
                new_targeted_vertices.remove(vertex_id)

            new_state = State(vertex_id, self._is_equipped, new_targeted_vertices,
                                           dict(self._kits_locations), self._graph)
            action = (ActionType.TRAVERSE, vertex_id)
            expand_state_list.append((new_state, action))

        new_kits_loc = dict(self._kits_locations)
        if self._is_equipped:
            new_kits_loc[self._current_vertex] = new_kits_loc.get(self._current_vertex, 0) + 1

            new_state = State(self._current_vertex, False, list(self._targeted_vertices),
                                           new_kits_loc, self._graph)
            action = (ActionType.UNEQUIP,)
            expand_state_list.append((new_state, action))
        else:
            if new_kits_loc.get(self._current_vertex , 0) > 0:
                new_kits_loc[self._current_vertex] = new_kits_loc.get(self._current_vertex, 0) - 1

                new_state = State(self._current_vertex, True, list(self._targeted_vertices),
                                               new_kits_loc, self._graph)
                action = (ActionType.EQUIP,)
                expand_state_list.append((new_state, action))

        return expand_state_list

    def mst_heuristic(self, simulator) -> float:

        precomputed_dijkstra = simulator._pre_computed_dijkstra_for_targets
        targets = set(self._targeted_vertices)
        if not targets:
            return 0.0

        current = self._current_vertex

        import math
        key = {}
        in_mst = set()

        for t in targets:
            if t not in precomputed_dijkstra:
                key[t] = math.inf
                continue
            dist_t, _ = precomputed_dijkstra[t]
            key[t] = dist_t.get(current, math.inf)

        mst = 0.0

        while len(in_mst) < len(targets):
            candidate = None
            candidate_key = math.inf
            for t in targets:
                if t in in_mst:
                    continue
                if key[t] < candidate_key:
                    candidate_key = key[t]
                    candidate = t

            if candidate is None or candidate_key == math.inf:
                return math.inf

            in_mst.add(candidate)
            mst += candidate_key

            dist_from_candidate, _ = precomputed_dijkstra[candidate]
            for t in targets:
                if t in in_mst:
                    continue
                d = dist_from_candidate.get(t, math.inf)
                if d < key[t]:
                    key[t] = d

        if not self._is_equipped:
            return mst

        P = simulator._kit_slowing_factor
        U = simulator._unequip_time

        # if is_equipped then stay equipped (all travel*P),
        # or unequip now and then travel without kit.
        return min(P * mst, mst + U)

    def get_key(self):
        return (
            self._current_vertex,
            self._is_equipped,
            tuple(sorted(self._targeted_vertices)),
            tuple(sorted(self._kits_locations.items())),
        )