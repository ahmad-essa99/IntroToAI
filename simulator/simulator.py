import math
from graph import Graph
from bayes_network import BayesNetwork
from bayes_network_node import BayesNetworkNode
from vertex import Vertex
from edge import Edge



class Simulator:
    def __init__(self, debug = True):
        self._num_of_vertices = 0
        self._p1_param = 0.0
        self._prior_dist_mild = 0.0
        self._prior_dist_stormy = 0.0
        self._prior_dist_extreme = 0.0

        self._graph = Graph()
        self._bayes_network = None
        self._debug = debug



    def print_world_state(self, agent):
        agent._score = agent._num_of_people_picked * 1000 - agent._agent_elapsed_time
        if self._debug:
            print(f"=========== Current world state ===========")
            print(f"Total evacuated people: {self._total_evacuated_people}")
            print(f"Total elapsed time: {self._total_elapsed_time}")
            print(f"Current set of targeted vertices : {self._set_of_targeted_vertices}")
            print(f"Current Agent({agent._id}) score: {agent._score}")
            print()

    def start_agents_loop(self):
        while self._set_of_targeted_vertices and any(self._active_agents.values()):
            for agent in self._agents:
                if self._active_agents[agent._id]:
                    next_move = agent.make_move(self)
                    if self._debug:
                        print(f"Agent ({agent._id}) Current move is {next_move}")
                    self.handle_next_move(agent, next_move=next_move)
                    self.print_world_state(agent)


    def _handle_input_file_line(self, line):
        line_parts = line.split()
        line_header = line_parts[0]

        # handle global constants
        if line_header == "#V":
            self._num_of_vertices = int(line_parts[1])

            for i in range(self._num_of_vertices):
                self._graph.add_vertex(Vertex(id=i+1))

        elif line_header == "#P1":
            self._p1_param = float(line_parts[1])
        elif line_header == "#W":
            self._prior_dist_mild = float(line_parts[1])
            self._prior_dist_stormy = float(line_parts[2])
            self._prior_dist_extreme = float(line_parts[3])

        elif line_header.startswith("#E"):
            edge_id = int(line_header[2:])

            v1 = int(line_parts[1])
            v2 = int(line_parts[2])

            weight = int(line_parts[3][1:])
            flooded_prob_given_mild = 0.0
            if len(line_parts) == 6 and line_parts[4] == "F":
                flooded_prob_given_mild = float(line_parts[5])

            current_edge = Edge(edge_id, v1, v2,
                                weight=weight, flooded_prob_given_mild=flooded_prob_given_mild)
            self._graph.add_edge(current_edge)

    def build_bayes_net(self):

        graph = self._graph
        bn = BayesNetwork()

        W = BayesNetworkNode("W", parents=[])
        W.set_cpt({
            "mild": float(self._prior_dist_mild),
            "stormy": float(self._prior_dist_stormy),
            "extreme": float(self._prior_dist_extreme)
        })
        bn.add_node(W)

        vertices_parents = {}
        for vertex_id in graph._vertices.keys():
            vertices_parents[vertex_id] = []

        for edge_id, edge in graph._edges.items():
            f_name = f"F_{edge_id}"
            weight = float(edge._weight)
            q = 1.0 if weight <= 0.0 else min(1.0, self._p1_param / weight)

            p_mild = float(edge._flooded_prob_given_mild)
            p_stormy = float(edge._flooded_prob_given_stormy)
            p_extreme = float(edge._flooded_prob_given_extreme)

            F = BayesNetworkNode(f_name, parents=["W"])
            F.set_cpt({
                "mild": {True: p_mild, False: 1.0 - p_mild},
                "stormy": {True: p_stormy, False: 1.0 - p_stormy},
                "extreme": {True: p_extreme, False: 1.0 - p_extreme},
            })
            bn.add_node(F)

            vertices_parents[edge._v1].append((f_name, q))
            vertices_parents[edge._v2].append((f_name, q))

        for vertex_id in graph._vertices.keys():
            ev_name = f"Ev_{vertex_id}"

            parent_pairs = vertices_parents[vertex_id]
            parent_pairs.sort(key=lambda x: x[0])
            parents = [p[0] for p in parent_pairs]
            q_list = [p[1] for p in parent_pairs]

            if len(parents) == 0:
                Ev = BayesNetworkNode(ev_name, parents=[])
                Ev.set_cpt({False: 1.0, True: 0.0})
                bn.add_node(Ev)
                continue

            cpt = {}

            all_false_vals = [(parent, False) for parent in parents]
            cpt[tuple(all_false_vals.copy())] = {True: 0.0, False: 1.0}

            for i in range(len(parents)):
                vals = all_false_vals.copy()

                vals[i] = (vals[i][0], True)
                qi = q_list[i]
                cpt[tuple(vals.copy())] = {True: 1.0 - qi, False: qi}

            Ev = BayesNetworkNode(ev_name, parents=parents)
            Ev.set_cpt(cpt)
            Ev.q_list = q_list
            bn.add_node(Ev)

        self._bayes_network = bn
        return bn








