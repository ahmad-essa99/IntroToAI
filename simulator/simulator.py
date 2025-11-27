import math
from graph import Graph
from enums import ActionType
from greedy_agent import GreedyAgent
from enums import AgentType
from vertex import Vertex
from edge import Edge
from agent import Agent
from human_agent import HumanAgent
from a_star_agent import A_StarAgent
from rl_a_star_agent import RealTime_A_StarAgent
from stupid_greedy_agent import StupidGreedyAgent


class Simulator:
    def __init__(self):
        self._num_of_vertices = 0
        self._equip_time = 0
        self._unequip_time = 0
        self._kit_slowing_factor = 0
        self._graph = Graph()
        self._num_of_agents = 0
        self._agents = []
        self._active_agents = {}
        self._total_evacuated_people = 0
        self._total_elapsed_time = 0
        self._pre_computed_dijkstra_for_targets = {}
        self._set_of_targeted_vertices = []
        self._kits_locations = dict()

    def test_init(self, agent_types_and_loc):
        self._set_of_targeted_vertices = sorted(self._set_of_targeted_vertices)
        self.run_dijkstra_for_every_target()
        self.test_init_agents(agent_types_and_loc)

    def init_sim(self):
        self._set_of_targeted_vertices = sorted(self._set_of_targeted_vertices)
        self.run_dijkstra_for_every_target()
        self.temp_init_agents() # i need to replace it with user prompt


    def run_dijkstra_for_every_target(self):
        # we don't have agent here , but we run dijkstra on a graph
        # were there is not flooded edges (relaxed graph)

        for target_vertex in self._set_of_targeted_vertices:
            dist, prev = self._graph._shortest_path_with_simple_dijkstra(
                source_vertex=target_vertex, agent_is_equipped=True)
            self._pre_computed_dijkstra_for_targets[target_vertex] = (dist, prev)

    def check_if_valid_traverse_move(self, agent, next_vertex):
        if not self._graph.is_connected(agent._current_vertex, next_vertex):
            print(f"vertices {agent._current_vertex} and {next_vertex} are not connected")
            return False

        chosen_edge = self._graph.get_edge(agent._current_vertex, next_vertex)
        is_equipped_agent = agent._is_equipped
        is_flooded_edge = chosen_edge._is_flooded

        print(f"Edge ({chosen_edge._id}) is Flooded?: {is_flooded_edge}")

        # if agent is equipped return true always, if not -> i need to check if edge is flooded
        return is_equipped_agent or not is_flooded_edge

    def handle_traverse_move(self, agent, next_vertex_id):
        if not self.check_if_valid_traverse_move(agent, next_vertex_id):
            print("invalid traverse move")
            self.handle_no_op_move(agent)
            return
        print()

        chosen_edge = self._graph.get_edge(agent._current_vertex, next_vertex_id)
        agent.update_current_vertex(next_vertex_id)
        agent.increase_num_of_actions()
        step_time = chosen_edge._weight if not agent._is_equipped else chosen_edge._weight*self._kit_slowing_factor
        agent.increase_elapsed_time(step_time)
        self._total_elapsed_time+=step_time

        next_vertex = self._graph._vertices[next_vertex_id]
        if next_vertex._num_of_people > 0:
            agent._num_of_people_picked += next_vertex._num_of_people
            self._total_evacuated_people += next_vertex._num_of_people
            next_vertex._num_of_people = 0
            self._set_of_targeted_vertices.remove(next_vertex_id)

    def handle_equip_move(self, agent):
        if agent._is_equipped:
            print(f"Agent({agent._id}) already equipped")
            self.handle_no_op_move(agent)
            return

        if self._kits_locations.get(agent._current_vertex, 0) < 1:
            print(f"Current Vertex does not have a Kit to equip")
            self.handle_no_op_move(agent)
            return

        self._kits_locations[agent._current_vertex] = (
                self._kits_locations.get(agent._current_vertex, 0) - 1)
        agent._is_equipped = True
        agent.increase_elapsed_time(self._equip_time)
        self._total_elapsed_time += self._equip_time
        agent.increase_num_of_actions()

    def handle_unequip_move(self, agent):
        if not agent._is_equipped:
            print(f"Agent({agent._id}) is not equipped")
            self.handle_no_op_move(agent)
            return

        self._kits_locations[agent._current_vertex] = (
                self._kits_locations.get(agent._current_vertex, 0) + 1)
        agent._is_equipped = False
        agent.increase_elapsed_time(self._unequip_time)
        self._total_elapsed_time += self._unequip_time
        agent.increase_num_of_actions()

    def handle_no_op_move(self, agent):
        print("No operation was choosed or forced")
        agent.increase_elapsed_time(1)
        self._total_elapsed_time += 1

    def handle_next_move(self, agent, next_move):
        if next_move[0] == ActionType.TRAVERSE and len(next_move) == 2:
            self.handle_traverse_move(agent=agent, next_vertex_id=next_move[1])

        elif next_move[0] == ActionType.EQUIP:
            self.handle_equip_move(agent)

        elif next_move[0] == ActionType.UNEQUIP:
            self.handle_unequip_move(agent)

        elif next_move[0] == ActionType.TERMINATE:
            self._active_agents[agent._id] = False
            print(f"agent {agent._agent_type} ({agent._id}) Terminated")

        else:
            self.handle_no_op_move(agent)

    def print_world_state(self, agent):
        print(f"=========== Current world state ===========")
        print(f"Total evacuated people: {self._total_evacuated_people}")
        print(f"Total elapsed time: {self._total_elapsed_time}")
        print(f"Current set of targeted vertices : {self._set_of_targeted_vertices}")
        print(f"Current Agent({agent._id}) score: {agent._num_of_people_picked*1000 - agent._agent_elapsed_time}")
        print()

    def start_agents_loop(self):
        while self._set_of_targeted_vertices and any(self._active_agents.values()):
            for agent in self._agents:
                if self._active_agents[agent._id]:
                    next_move = agent.make_move(self)
                    print(f"Agent ({agent._id}) Current move is {next_move}")
                    self.handle_next_move(agent, next_move=next_move)
                    self.print_world_state(agent)

    def test_init_agents(self, agent_types_and_loc):
        self._num_of_agents = len(agent_types_and_loc)
        curr_id = 1
        agent = None
        for agent_type, agent_loc in agent_types_and_loc:
            if agent_type == AgentType.STUPID_GREEDY:
                agent = StupidGreedyAgent(curr_id, starting_vertex=agent_loc)
            elif agent_type == AgentType.GREEDY :
                agent = GreedyAgent(curr_id, starting_vertex=agent_loc)
            elif agent_type == AgentType.A_STAR :
                agent = A_StarAgent(curr_id, starting_vertex=agent_loc)
            elif agent_type == AgentType.REAL_TIME_A_STAR :
                agent = RealTime_A_StarAgent(curr_id, starting_vertex=agent_loc)
            curr_id+=1
            self._add_new_agent(agent)


    def temp_init_agents(self):
        self._num_of_agents = 1
        # human_agent = HumanAgent(1, starting_vertex=1)
        greedy_agent = RealTime_A_StarAgent(2, starting_vertex=1)
        # self._agents.append(human_agent)
        self._add_new_agent(greedy_agent)

    def _add_new_agent(self, new_agent):
        self._agents.append(new_agent)
        self._active_agents[new_agent._id] = True

        current_vertex = self._graph._vertices[new_agent._current_vertex]
        if current_vertex._num_of_people > 0:
            new_agent._num_of_people_picked += current_vertex._num_of_people
            self._total_evacuated_people += current_vertex._num_of_people
            current_vertex._num_of_people = 0
            self._set_of_targeted_vertices.remove(new_agent._current_vertex)
            self.print_world_state(new_agent)


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
            if len(line_parts) < 4:
                print("input file edge line is invalid")
                exit(1)

            edge_id = int(line_header[2:])

            v1 = int(line_parts[1])
            v2 = int(line_parts[2])

            weight = int(line_parts[3][1:])
            is_flooded = False
            if len(line_parts) == 5 and line_parts[4] == "F":
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





