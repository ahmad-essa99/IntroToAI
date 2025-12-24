import math
import time
from enum import Enum

from agent_state import AgentState


class Agent:
    def __init__(self, id: int, starting_vertex: int, debug=True):

        self._id = id
        self._current_vertex = starting_vertex
        self._num_of_people_picked = 0
        self._agent_elapsed_time = 0
        self._is_equipped = False
        self._busy_time = 0
        self.in_progress_action = None
        self.traverse_dest = None
        self._agent_type = None
        self._debug = debug

    def increase_elapsed_time(self, step_time):
        self._agent_elapsed_time += step_time

    def make_move(self, simulator):
        self.print_state()
        simulator._graph.print_vertex_info(self._current_vertex, simulator._kits_locations.get(self._current_vertex, 0),
                                           debug=self._debug)

        if self._debug:
            print()

    def print_state(self):
        if self._debug:
            print(f"=== {self._agent_type.value} Agent (ID {self._id}) ===")
            print(f"Current vertex       : {self._current_vertex}")
            print(f"People picked        : {self._num_of_people_picked}")
            print(f"Elapsed time         : {self._agent_elapsed_time}")
            print(f"Equipped with kit?   : {'Yes' if self._is_equipped else 'No'}")
            print("----------------------------")


    def get_agent_state(self):
        return AgentState(
            current_vertex=self._current_vertex,
            is_equipped=self._is_equipped,
            num_of_people_picked=self._num_of_people_picked,
            busy_time=self._busy_time,
            in_progress_action=self.in_progress_action,
            traverse_dest=self.traverse_dest,
        )