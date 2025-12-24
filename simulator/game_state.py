from enums import ActionType


class GameState:

    def __init__(self, simulator, first_agent_state, second_agent_state, target_vertices, kits_locations, turn, time):
        self.simulator = simulator
        self._agents_states = [first_agent_state, second_agent_state]

        self._target_vertices = dict(target_vertices)
        self._kits_locations = dict(kits_locations)

        self.turn = turn
        self.time = time

    def copy(self):
        return GameState(
            simulator=self.simulator,
            first_agent_state=self._agents_states[0].copy(),
            second_agent_state=self._agents_states[1].copy(),
            target_vertices=dict(self._target_vertices),
            kits_locations=dict(self._kits_locations),
            turn=self.turn,
            time=self.time,
        )


    def total_remaining_people(self):
        return sum(self._target_vertices.values())

    def is_terminal_state(self):
        if self.total_remaining_people() == 0:
            return True

        D = self.simulator._deadline_time
        if D is not None and self.time >= D:
            return True

        return False

    def _pickup_people_if_any(self, agent_idx):
        agent_state = self._agents_states[agent_idx]
        agent_current_vertex = agent_state._current_vertex

        c = self._target_vertices.get(agent_current_vertex, 0)
        if c > 0:
            agent_state._num_of_people_picked += c
            self._target_vertices[agent_current_vertex] = 0
            del self._target_vertices[agent_current_vertex]

    def legal_actions(self):
        agent_index = self.turn
        agent_state = self._agents_states[agent_index]

        if agent_state._busy_time > 0:
            return [(ActionType.NO_OP,)]

        actions = []

        agent_curr_vertex = agent_state._current_vertex
        neighbors = self.simulator._graph.expand(vertex_id=agent_curr_vertex, is_equipped=agent_state._is_equipped)
        actions = [(ActionType.TRAVERSE, neighbor) for neighbor in neighbors]


        if (not agent_state._is_equipped) and self._kits_locations.get(agent_curr_vertex, 0) > 0:
            actions.append((ActionType.EQUIP,))
        if agent_state._is_equipped:
            actions.append((ActionType.UNEQUIP,))

        actions.append((ActionType.NO_OP,))

        return actions

    def start_action(self, action):
        agent_index = self.turn
        agent_state = self._agents_states[agent_index]

        a0 = action[0]

        # TRAVERSE
        if a0 == ActionType.TRAVERSE and len(action) == 2:
            dest = int(action[1])
            duration = self.simulator._kit_slowing_factor if agent_state._is_equipped else 1
            agent_state._busy_time = duration
            agent_state.in_progress_action = ActionType.TRAVERSE
            agent_state.traverse_dest = dest
            return

        # EQUIP
        if a0 == ActionType.EQUIP:
            agent_curr_vertex = agent_state._current_vertex
            self._kits_locations[agent_curr_vertex] = self._kits_locations.get(agent_curr_vertex, 0) - 1
            agent_state._busy_time = self.simulator._equip_time
            agent_state.in_progress_action = ActionType.EQUIP
            agent_state.traverse_dest = None
            return

        # UNEQUIP
        if a0 == ActionType.UNEQUIP:
            agent_state._busy_time = self.simulator._unequip_time
            agent_state.in_progress_action = ActionType.UNEQUIP
            agent_state.traverse_dest = None
            return

        # NO_OP
        agent_state._busy_time = 1
        agent_state.in_progress_action = ActionType.NO_OP
        agent_state.traverse_dest = None
        return

    def advance_one_tick(self):

        agent_index = self.turn
        agent_state = self._agents_states[agent_index]

        if agent_state._busy_time > 0:
            agent_state._busy_time -= 1
            if agent_state._busy_time == 0:
                self._complete_action(agent_index)

        self.time += 1
        self.turn = 1 - self.turn

    def _complete_action(self, agent_index):
        agent_state = self._agents_states[agent_index]
        agent_current_action = agent_state.in_progress_action

        if agent_current_action == ActionType.TRAVERSE:
            agent_state._current_vertex = agent_state.traverse_dest
            agent_state.traverse_dest = None
            agent_state.in_progress_action = None
            self._pickup_people_if_any(agent_index)
            return

        if agent_current_action == ActionType.EQUIP:
            agent_state._is_equipped = True
            agent_state.in_progress_action = None
            return

        if agent_current_action == ActionType.UNEQUIP:
            agent_state._is_equipped = False
            agent_curr_vertex = agent_state._current_vertex
            self._kits_locations[agent_curr_vertex] = self._kits_locations.get(agent_curr_vertex, 0) + 1
            agent_state.in_progress_action = None
            return

        # NO_OP
        agent_state.in_progress_action = None
        agent_state.traverse_dest = None

    def get_next_state(self, action):

        next_game_state = self.copy()
        cur_agent = next_game_state._agents_states[next_game_state.turn]
        if cur_agent._busy_time > 0:
            next_game_state.advance_one_tick()
            return next_game_state

        next_game_state.start_action(action)
        next_game_state.advance_one_tick()
        return next_game_state

    def get_key(self):
        return (
            self.turn,
            self._agents_states[0].get_key(),
            self._agents_states[1].get_key(),
            tuple(sorted(self._target_vertices.items())),
            tuple(sorted(self._kits_locations.items()))
        )


