from graph import Graph
from agent import Agent, AgentType
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

    def temp_init_agents(self):
        self._num_of_agents = 1
        human_agent = Agent(1, agent_type=AgentType.HUMAN,
                            starting_vertex=1)
        self._agents.append(human_agent)

    def read_and_parse_input_file(self, input_file_path):
        with open(input_file_path, "r") as input_file:
            for line in input_file:
                line = line.strip()

                if not line:
                    continue

                if ";" in line:
                    line = line.split(";")[0].strip()

                # line is not empty and clean
                self._handle_input_file_line(line)

        if not self._num_of_vertices == len(self._graph._vertices):
            print("input file missmatch")
            exit(1)



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





