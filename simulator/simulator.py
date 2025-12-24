import math
from graph import Graph
from enums import ActionType
from enums import AgentType
from adversarial_agent import AdversarialAgent
from game_state import GameState
from vertex import Vertex
from edge import Edge
from agent import Agent

AGENTS_MAP = {AgentType.ADVERSARIAL: AdversarialAgent,
                AgentType.SEMI_COOPERATIVE: None,
                AgentType.FULLY_COOPERATIVE: None
       }


class Simulator:
    def __init__(self, debug = True):
        self._num_of_vertices = 0
        self._equip_time = 0
        self._unequip_time = 0
        self._kit_slowing_factor = 0
        self._deadline_time = 0
        self._graph = Graph()
        self._debug = debug
        self._total_evacuated_people = 0
        self._total_elapsed_time = 0
        self._set_of_targeted_vertices = []
        self._kits_locations = dict()
        self._num_of_agents = 2

        self._first_agent = None
        self._second_agent = None
        self._active_agents = {}
        self.turn = 0

    """
    1. added _busy_time to Agent Class 
        added in_progress_action and traverse_dest to Agent also
        
    2. added _deadline_time _first_agent and _second_agent and self.turn to Simulator class 
    """

    def get_game_state(self):
        return GameState(
            simulator=self,
            first_agent_state=self._first_agent.get_agent_state(),
            second_agent_state=self._second_agent.get_agent_state(),
            target_vertices=self._graph.get_target_vertices(),
            kits_locations=self._kits_locations,
            turn=self.turn,
            time=self._total_elapsed_time
        )

    def test_init(self, agent_types_and_loc):
        self._set_of_targeted_vertices = sorted(self._set_of_targeted_vertices)
        self.run_dijkstra_for_every_target()
        self._init_agents(agent_types_and_loc)

    def init_sim(self, agents_types, first_agent_loc, sec_agent_loc):
        self._set_of_targeted_vertices = sorted(self._set_of_targeted_vertices)
        # self.run_dijkstra_for_every_target()
        self._init_agents(agents_types, first_agent_loc, sec_agent_loc)


    def _init_agents(self, agents_types, first_agent_loc, sec_agent_loc):
        curr_id = 0
        agent_class = AGENTS_MAP.get(agents_types)
        assert not agent_class == None, "you choosed wrong agent type"

        self._first_agent = agent_class(curr_id, starting_vertex=first_agent_loc, debug=self._debug)
        curr_id+=1
        self._second_agent = agent_class(curr_id, starting_vertex=sec_agent_loc, debug=self._debug)
        self._add_new_agent(self._first_agent)
        self._add_new_agent(self._second_agent)


    def _add_new_agent(self, new_agent):
        self._active_agents[new_agent._id] = True

        current_vertex = self._graph._vertices[new_agent._current_vertex]
        if current_vertex._num_of_people > 0:
            new_agent._num_of_people_picked += current_vertex._num_of_people
            self._total_evacuated_people += current_vertex._num_of_people
            current_vertex._num_of_people = 0
            self._set_of_targeted_vertices.remove(new_agent._current_vertex)
            self.print_world_state(new_agent)


    def run_dijkstra_for_every_target(self):
        # we don't have agent here , but we run dijkstra on a graph
        # were there is not flooded edges (relaxed graph)

        for target_vertex in self._set_of_targeted_vertices:
            dist, prev = self._graph._shortest_path_with_simple_dijkstra(
                source_vertex=target_vertex, agent_is_equipped=True)
            self._pre_computed_dijkstra_for_targets[target_vertex] = (dist, prev)

    def start_agents_loop(self):
        seen_states = set()

        while True:

            if not self._set_of_targeted_vertices:
                print("no remaining target_vertices, break the loop")
                break

            if self._total_elapsed_time >= self._deadline_time:
                print("dead line time reached, break the loop")
                break

            game_state = self.get_game_state()
            state_key = game_state.get_key()
            if state_key in seen_states:
                print("cycle state detected, break the loop")
                break
            seen_states.add(state_key)

            agent = self._first_agent if self.turn == 0 else self._second_agent

            agent_next_move = agent.make_move(self)
            if self._debug:
                print(f"Agent ({agent._id}) Current move is {agent_next_move}")

            self._start_next_move(agent, agent_next_move)
            self._advance_one_tick_for_agent(agent)

            self._total_elapsed_time += 1
            self.turn = 1 - self.turn
            self.print_world_state(agent)

    def _advance_one_tick_for_agent(self, agent):
        if agent._busy_time <= 0:
            return

        agent._busy_time -= 1

        if agent._busy_time == 0:
            self._complete_action(agent)

    def _complete_action(self, agent):

        current_action = agent.in_progress_action

        if current_action == ActionType.TRAVERSE:
            agent._current_vertex = agent.traverse_dest
            agent.traverse_dest = None
            agent.in_progress_action = None

            next_vertex = self._graph._vertices[agent._current_vertex]
            if next_vertex._num_of_people > 0:
                agent._num_of_people_picked += next_vertex._num_of_people
                self._total_evacuated_people += next_vertex._num_of_people
                next_vertex._num_of_people = 0
                self._set_of_targeted_vertices.remove(agent._current_vertex)
            return

        if current_action == ActionType.EQUIP:
            agent._is_equipped = True
            agent.in_progress_action = None
            return

        if current_action == ActionType.UNEQUIP:
            agent._is_equipped = False
            self._kits_locations[agent._current_vertex] = self._kits_locations.get(
                agent._current_vertex, 0) + 1
            agent.in_progress_action = None
            return


        agent.in_progress_action = None
        agent.traverse_dest = None

    def _start_next_move(self, agent, next_move):
        if agent._busy_time > 0:
            return

        action_type = next_move[0]

        if action_type == ActionType.TRAVERSE and len(next_move) == 2:
            dest = int(next_move[1])
            if not self.check_if_valid_traverse_move(agent, dest):
                self._start_no_op(agent)
                return

            agent._busy_time = self._kit_slowing_factor if agent._is_equipped else 1
            agent.in_progress_action = ActionType.TRAVERSE
            agent.traverse_dest = dest
            return


        if action_type == ActionType.EQUIP:
            v = agent._current_vertex

            if agent._is_equipped or self._kits_locations.get(v, 0) <= 0:
                self._start_no_op(agent)
                return
            self._kits_locations[v] = self._kits_locations.get(v, 0) - 1

            agent._busy_time = self._equip_time
            agent.in_progress_action = ActionType.EQUIP
            agent.traverse_dest = None
            return

        if action_type == ActionType.UNEQUIP:
            if not agent._is_equipped:
                self._start_no_op(agent)
                return

            agent._busy_time = self._unequip_time
            agent.in_progress_action = ActionType.UNEQUIP
            agent.traverse_dest = None
            return

        self._start_no_op(agent)

    def _start_no_op(self, agent):
        agent.in_progress_action = ActionType.NO_OP
        agent.traverse_dest = None
        agent._busy_time = 1


    def check_if_valid_traverse_move(self, agent, next_vertex):
        if not self._graph.is_connected(agent._current_vertex, next_vertex):
            print(f"vertices {agent._current_vertex} and {next_vertex} are not connected")
            return False

        chosen_edge = self._graph.get_edge(agent._current_vertex, next_vertex)
        is_equipped_agent = agent._is_equipped
        is_flooded_edge = chosen_edge._is_flooded

        if self._debug:
            print(f"Edge ({chosen_edge._id}) is Flooded?: {is_flooded_edge}")

        return is_equipped_agent or not is_flooded_edge


    def print_world_state(self, agent):
        agent._score = agent._num_of_people_picked * 1000 - agent._agent_elapsed_time
        if self._debug:
            print(f"=========== Current world state ===========")
            print(f"Total evacuated people: {self._total_evacuated_people}")
            print(f"Total elapsed time: {self._total_elapsed_time}")
            print(f"Current set of targeted vertices : {self._set_of_targeted_vertices}")
            print(f"Current Agent({agent._id}) score: {agent._score}")
            print()


    def _handle_input_file_line(self, line):
        line_parts = line.split()
        line_header = line_parts[0]

        # handle global constants
        if line_header == "#N":
            self._num_of_vertices = int(line_parts[1])
        elif line_header == "#U":
            self._unequip_time = int(line_parts[1])
        elif line_header == "#Q":
            self._equip_time = int(line_parts[1])
        elif line_header == "#P":
            self._kit_slowing_factor = int(line_parts[1])
        elif line_header == "#D":
            self._deadline_time = int(line_parts[1])

        # handle vertex case
        elif line_header.startswith("#V"):
            vertex_id = int(line_header[2:])
            num_people = 0
            num_kits = 0

            for token in line_parts[1:]:
                if token == "K":
                    num_kits = 1
                elif token.startswith("P"):
                    num_people = int(token[1:])

            current_vertex = Vertex(vertex_id, num_of_people=num_people)
            if num_kits > 0:
                self._kits_locations[vertex_id] = num_kits
            self._graph.add_vertex(current_vertex)

            if current_vertex._num_of_people > 0:
                self._set_of_targeted_vertices.append(vertex_id)

        elif line_header.startswith("#E"):
            if len(line_parts) < 3:
                print("input file edge line is invalid")
                exit(1)

            edge_id = int(line_header[2:])

            v1 = int(line_parts[1])
            v2 = int(line_parts[2])

            weight = 1
            is_flooded = False
            if len(line_parts) == 4 and line_parts[3] == "F":
                is_flooded = True

            current_edge = Edge(edge_id, v1, v2,
                                weight=weight, is_flooded=is_flooded)
            self._graph.add_edge(current_edge)

    def step_cost(self, current_vertex_id, is_equipped, action):
        action_type = action[0]

        if action_type == ActionType.TRAVERSE:
            _, next_vertex = action
            edge_weight = self._graph.get_edge(current_vertex_id, next_vertex)._weight

            if is_equipped:
                return edge_weight * self._kit_slowing_factor
            else:
                return edge_weight

        elif action_type == ActionType.EQUIP:
            return self._equip_time

        elif action_type == ActionType.UNEQUIP:
            return self._unequip_time

        elif action_type == ActionType.NO_OP:
            return 1.0

        elif action_type == ActionType.TERMINATE:
            return 0.0

        return math.inf





