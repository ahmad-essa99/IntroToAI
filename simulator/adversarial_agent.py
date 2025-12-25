

import math
from enums import ActionType
from enums import AgentType
from agent import Agent



class AdversarialAgent(Agent):

    def __init__(self, id, starting_vertex, depth_limit=10, debug=True):
        super().__init__(id=id, starting_vertex=starting_vertex, debug=debug)
        self._agent_type = AgentType.ADVERSARIAL
        self._depth_limit = depth_limit

    def make_move(self, simulator):
        super().make_move(simulator)

        if self._busy_time > 0:
            return (ActionType.NO_OP,)

        current_game_state = simulator.get_game_state()
        actions = current_game_state.legal_actions()

        best_action = actions[0]
        best_value = -math.inf
        alpha = -math.inf
        beta = math.inf

        for action in actions:
            successor = current_game_state.get_next_state(action)
            v = self._min_value(successor, depth=1, alpha=alpha, beta=beta)

            if v > best_value:
                best_value = v
                best_action = action

            alpha = max(alpha, best_value)

        return best_action

    def _max_value(self, state, depth, alpha, beta):
        assert state.turn == self._id

        if state.is_terminal_state() or depth >= self._depth_limit:
            return self._evaluate(state)

        actions = state.legal_actions()
        v = -math.inf
        for action in actions:
            successor = state.get_next_state(action)
            v = max(v, self._min_value(successor, depth + 1, alpha, beta))

            if v >= beta:
                return v
            alpha = max(alpha, v)

        return v

    def _min_value(self, state, depth, alpha, beta):
        assert state.turn != self._id

        if state.is_terminal_state() or depth >= self._depth_limit:
            return self._evaluate(state)

        actions = state.legal_actions()
        v = math.inf
        for action in actions:
            successor = state.get_next_state(action)
            v = min(v, self._max_value(successor, depth + 1, alpha, beta))

            if v <= alpha:
                return v
            beta = min(beta, v)

        return v

    def _evaluate(self, game_state):

        current_agent_id = self._id
        other_agent_id = 1 - current_agent_id
        my_saved = game_state._agents_states[current_agent_id]._num_of_people_picked
        other_saved = game_state._agents_states[other_agent_id]._num_of_people_picked
        return my_saved - other_saved




