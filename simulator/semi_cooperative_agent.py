from enums import ActionType, AgentType
from agent import Agent


class SemiCooperativeAgent(Agent):
    def __init__(self, id, starting_vertex, depth_limit=10, debug=True):
        super().__init__(id=id, starting_vertex=starting_vertex, debug=debug)
        self._agent_type = AgentType.SEMI_COOPERATIVE
        self._depth_limit = depth_limit

    def make_move(self, simulator):
        super().make_move(simulator)

        if self._busy_time > 0:
            return (ActionType.NO_OP,)

        state = simulator.get_game_state()
        actions = state.legal_actions()


        best_action = actions[0]
        best_pair = None # pair (IS0, IS1)

        for action in actions:
            successor = state.get_next_state(action)
            pair = self._semi_value(successor, depth=1)

            if best_pair is None or self._prefer(pair, best_pair, chooser_id=self._id):
                best_pair = pair
                best_action = action

        return best_action

    def _semi_value(self, game_state, depth):
        if game_state.is_terminal_state() or depth >= self._depth_limit:
            return self._eval_leaf_state(game_state)

        actions = game_state.legal_actions()
        chooser = game_state.turn
        best = None
        for action in actions:
            successor = game_state.get_next_state(action)
            pair = self._semi_value(successor, depth + 1)

            if best is None or self._prefer(pair, best, chooser_id=chooser):
                best = pair

        return best

    def _eval_leaf_state(self, game_state):
        first_saved = game_state._agents_states[0]._num_of_people_picked
        second_saved = game_state._agents_states[1]._num_of_people_picked
        return (first_saved, second_saved) # IS0, IS1

    def _prefer(self, new_pair, curr_best_pair, chooser_id):

        new_IS0, new_IS1 = new_pair
        curr_best_IS0, curr_best_IS1 = curr_best_pair

        if chooser_id == 0:
            # maximize IS0, break tie by IS1
            if new_IS0 != curr_best_IS0:
                return new_IS0 > curr_best_IS0
            return new_IS1 > curr_best_IS1
        else:
            # maximize IS1, break tie by IS0
            if new_IS1 != curr_best_IS1:
                return new_IS1 > curr_best_IS1
            return new_IS0 > curr_best_IS0

