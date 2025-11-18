from Scripts.activate_this import abs_file

from graph import Graph
from agent import Agent, AgentType
from human_agent import HumanAgent
from enums import ActionType
from greedy_agent import GreedyAgent
from vertex import Vertex
from edge import Edge


class Simulator:
    def __init__(self):
        self._num_of_vertices = 0
        self._equip_time = 0
        self._unequip_time = 0
        self._kit_slowing_factor = 0

        self._graph = Graph()
        self._set_of_targeted_vertices = []
        self._num_of_agents = 0
        self._agents = []
        self._total_evacuated_people = 0
        self._total_elapsed_time = 0

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

        current_vertex = self._graph._vertices[agent._current_vertex]
        if current_vertex._num_of_kits < 1:
            print(f"Current Vertex does not have a Kit to equip")
            self.handle_no_op_move(agent)
            return

        current_vertex._num_of_kits -=1
        agent._is_equipped = True
        agent.increase_elapsed_time(self._equip_time)
        self._total_elapsed_time += self._equip_time

    def handle_unequip_move(self, agent):
        if not agent._is_equipped:
            print(f"Agent({agent._id}) is not equipped")
            self.handle_no_op_move(agent)
            return

        current_vertex = self._graph._vertices[agent._current_vertex]
        current_vertex._num_of_kits += 1
        agent._is_equipped = False
        agent.increase_elapsed_time(self._unequip_time)
        self._total_elapsed_time += self._unequip_time

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

        else:
            self.handle_no_op_move(agent)



    def print_world_state(self, agent):
        print(f"=========== Current world state ===========")
        print(f"Total evacuated people: {self._total_evacuated_people}")
        print(f"Total elapsed time: {self._total_elapsed_time}")
        print(f"Current set of targeted vertices : {self._set_of_targeted_vertices}")
        print(f"Current Agent({agent._id} score: {agent._num_of_people_picked*1000 - agent._agent_elapsed_time})")
        print()

    def start_agents_loop(self):
        while self._set_of_targeted_vertices:
            for agent in self._agents:
                next_move = agent.make_move(self)
                print(f"Agent ({agent._id}) Current move is {next_move}")
                self.handle_next_move(agent, next_move=next_move)
                self.print_world_state(agent)

    def temp_init_agents(self):
        self._num_of_agents = 1
        # human_agent = HumanAgent(1, starting_vertex=1)
        greedy_agent = GreedyAgent(2, starting_vertex=1)
        # self._agents.append(human_agent)
        self._agents.append(greedy_agent)

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

            current_vertex = Vertex(vertex_id, num_of_kits=num_kits, num_of_people=num_people)
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





