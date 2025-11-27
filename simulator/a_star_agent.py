import heapq
import math
from enums import ActionType, AgentType
from Node import Node
from state import State
from agent import Agent

LIMIT = 10000

class A_StarAgent(Agent):
    def __init__(self, id: int, starting_vertex: int):
        super().__init__(id, starting_vertex)
        self._agent_type = AgentType.A_STAR
        self._current_plan = []
        self._current_goal_vertex = None
        self._over_all_targets_sets = None

    def make_move(self, simulator):
        super().make_move(simulator)

        self._over_all_targets_sets =  list(set(simulator._set_of_targeted_vertices)
                                                    & set(self._set_of_reachable_targets))

        if not self._over_all_targets_sets:
            print(f"{self._agent_type}: no target vertices left -> TERMINATE")
            return (ActionType.TERMINATE,)

        if self._current_plan and self._current_goal_vertex in self._over_all_targets_sets:
            action = self._current_plan.pop(0)
            return action

        self._current_plan = []
        self._current_goal_vertex = None
        plan = self._run_a_star(simulator)

        if plan is None:
            return (ActionType.TERMINATE,)

        self._current_plan = plan
        action = plan.pop(0)
        return action


    def _run_a_star(self, simulator):
        start_state = State(
            current_vertex=self._current_vertex,
            is_equipped=self._is_equipped,
            targeted_vertices=list(self._over_all_targets_sets),
            kits_locations=dict(simulator._kits_locations),
            graph=simulator._graph,
        )

        start_node = Node(start_state, g=0.0, parent=None, action=None)
        start_node.compute_h(simulator)
        if math.isinf(start_node.h):
            return None

        OPEN = []
        CLOSED = {}
        counter = 0
        expansions = 0

        heapq.heappush(OPEN, (start_node.f, counter, start_node))

        while True:

            # if OPEN is empty then return failure
            if not OPEN:
                return None

            # node = Remove-Front(OPEN)
            _, _, node = heapq.heappop(OPEN)

            # Goal test
            if not node.state._targeted_vertices:
                return self._reconstruct_plan(node)

            # expansion limit test
            expansions += 1
            if expansions >= LIMIT:
                print(f"AStarAgent: reached LIMIT={LIMIT} expansions, aborting.")
                return None

            # if no node’ in CLOSED with state(current_node)=state(node’)
            #  or exists such a node’ in CLOSED with f(current_node) < f(node’))
            # then expand, else skip

            state_key = node.state.get_key()
            if node.f >= CLOSED.get(state_key, math.inf):
                continue

            CLOSED[state_key] = node.f

            for child in node.expand(simulator):
                counter += 1
                heapq.heappush(OPEN, (child.f, counter, child))


