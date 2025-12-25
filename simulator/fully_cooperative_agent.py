

import math
from enums import ActionType
from enums import AgentType
from agent import Agent



class FullyCooperativeAgent(Agent):

    def __init__(self, id, starting_vertex, depth_limit=10, debug=True):
        super().__init__(id=id, starting_vertex=starting_vertex, debug=debug)
        self._agent_type = AgentType.FULLY_COOPERATIVE
        self._depth_limit = depth_limit

    def make_move(self, simulator):
        super().make_move(simulator)

        if self._busy_time > 0:
            return (ActionType.NO_OP,)

        current_game_state = simulator.get_game_state()
        actions = current_game_state.legal_actions()

        best_action = actions[0]
        best_value = -math.inf

        for action in actions:
            successor = current_game_state.get_next_state(action)
            v = self._max_value(successor, depth=1)

            if v > best_value:
                best_value = v
                best_action = action


        return best_action

    def _max_value(self, state, depth):
        if state.is_terminal_state() or depth >= self._depth_limit:
            return self._evaluate(state)

        actions = state.legal_actions()
        v = -math.inf
        for action in actions:
            successor = state.get_next_state(action)
            v = max(v, self._max_value(successor, depth + 1))

        return v

    def _evaluate(self, game_state):
        first_saved = game_state._agents_states[0]._num_of_people_picked
        second_saved = game_state._agents_states[1]._num_of_people_picked
        return first_saved + second_saved




