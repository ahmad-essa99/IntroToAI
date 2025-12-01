import math
from agent import Agent
from enums import ActionType, AgentType
from state import State


class GreedyAgent(Agent):
    def __init__(self, id: int, starting_vertex: int):
        super().__init__(id, starting_vertex)
        self._agent_type = AgentType.GREEDY

    def make_move(self, simulator):
        super().make_move(simulator)

        over_all_targets_sets =  list(set(simulator._set_of_targeted_vertices)
                                                    & set(self._set_of_reachable_targets))

        if not over_all_targets_sets:
            print(f"{self._agent_type}: no target vertices left -> TERMINATE")
            return (ActionType.TERMINATE,)

        current_state = State(
            current_vertex=self._current_vertex,
            is_equipped=self._is_equipped,
            targeted_vertices=list(over_all_targets_sets),
            kits_locations=dict(simulator._kits_locations),
            graph=simulator._graph,
        )

        successors = current_state.expand()
        if not successors:
            print("GreedyAgent: no successors -> TERMINATE")
            return (ActionType.TERMINATE,)

        best_state = None
        best_action = None
        best_h = math.inf

        for (succ_state, action) in successors:
            h = succ_state.mst_heuristic(simulator)
            if self._debug:
                print(f"  successor: v={succ_state._current_vertex}, "
                      f"equipped={succ_state._is_equipped}, h={h}, action={action}")

            if h < best_h:
                best_h = h
                best_state = succ_state
                best_action = action

            # tie break if h is the same, choose lower vertex id
            elif h == best_h:
                if (action[0] == ActionType.TRAVERSE == best_action[0]):
                    if action[1] < best_action[1]:
                        best_state = succ_state
                        best_action = action

        if best_state is None or best_action is None or math.isinf(best_h):
            print("GreedyAgent: all successors have infinite heuristic -> NO_OP")
            return (ActionType.TERMINATE,)
        if self._debug:
            print(f"GreedyAgent chooses action: {best_action}, heuristic={best_h}")
        return best_action




