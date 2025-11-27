import math
import time
from enum import Enum


class Agent:
    def __init__(self, id: int, starting_vertex: int):

        self._id = id
        self._current_vertex = starting_vertex
        self._num_of_people_picked = 0
        self._num_of_actions = 0
        self._agent_elapsed_time = 0
        self._is_equipped = False
        self._agent_type = None
        self._reachable_targets_is_set = False
        self._set_of_reachable_targets = []

    def update_current_vertex(self, new_vertex):
        self._current_vertex = new_vertex

    def increase_num_of_actions(self):
        self._num_of_actions+=1

    def increase_elapsed_time(self, step_time):
        self._agent_elapsed_time += step_time

    def make_move(self, simulator):
        self.print_state()
        simulator._graph.print_vertex_info(self._current_vertex, simulator._kits_locations.get(self._current_vertex, 0))

        if not self._reachable_targets_is_set:
            self._iniaite_reachable_targets_set(simulator)

        print()

    def _iniaite_reachable_targets_set(self, simulator):

        if simulator._kits_locations.get(self._current_vertex,0) > 0:
            dist, _ = simulator._graph._shortest_path_with_simple_dijkstra(
                self._current_vertex, agent_is_equipped=True)
        else:
            dist, _ = simulator._graph._shortest_path_with_simple_dijkstra(
                self._current_vertex, agent_is_equipped=False)

            for vertex_id in dist.keys():
                if (vertex_id != self._current_vertex and
                        dist[vertex_id] != math.inf and simulator._kits_locations.get(vertex_id, 0) > 0):
                    dist, _ = simulator._graph._shortest_path_with_simple_dijkstra(
                        self._current_vertex, agent_is_equipped=True)
                    break

        for target_vertex in simulator._set_of_targeted_vertices:
            if dist[target_vertex] != math.inf:
                self._set_of_reachable_targets.append(target_vertex)

        self._reachable_targets_is_set = True
        print(f"reachable targets are {self._set_of_reachable_targets}")

    def print_state(self):
        print(f"=== {self._agent_type.value} Agent (ID {self._id}) ===")
        print(f"Current vertex       : {self._current_vertex}")
        print(f"People picked        : {self._num_of_people_picked}")
        print(f"Total actions done   : {self._num_of_actions}")
        print(f"Elapsed time         : {self._agent_elapsed_time}")
        print(f"Equipped with kit?   : {'Yes' if self._is_equipped else 'No'}")
        print("----------------------------")

    def _reconstruct_plan(self, end_node, save_as_goal=True):
        actions = []
        if save_as_goal:
            self._current_goal_vertex = end_node.state._current_vertex
        node = end_node

        while node.parent is not None:
            actions.append(node.action)
            node = node.parent

        actions.reverse()
        return actions