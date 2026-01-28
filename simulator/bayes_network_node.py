class BayesNetworkNode:

    def __init__(self, name, parents):
        self.name = name
        self.states = ["mild", "stormy", "extreme"]
        self.q_list = []
        if not name == "W":
            self.states = [False, True]

        self.parents = parents
        self.cpt = {}

    def set_cpt(self, cpt_dict):
        # cpt_dict: {parent_tuple: {state: prob}}
        self.cpt = cpt_dict

    def print(self):
        if self.name == "W":
            self._print_weather()
        elif self.name.startswith("F_"):
            self._print_flooding_edge()
        elif self.name.startswith("Ev_"):
            self._print_evacuees_vertex()
        else:
            raise Exception("BNN type Error")

    def _print_weather(self):
        print("WEATHER:")
        print(f"  P(mild) = {self.cpt['mild']}")
        print(f"  P(stormy) = {self.cpt['stormy']}")
        print(f"  P(extreme) = {self.cpt['extreme']}")
        print()

    def _print_flooding_edge(self):
        edge_id = int(self.name.split("_")[1])

        print(f"EDGE {edge_id}:")
        for w in ["mild", "stormy", "extreme"]:
            p_flooded = self.cpt[w][True]
            print(f"  P(flooded|{w}) = {p_flooded:g}")
        print()


    def _print_evacuees_vertex(self):
        import itertools

        v_id = int(self.name.split("_")[1])
        print(f"VERTEX {v_id}:")

        if not self.parents:
            print("  P(Evacuees) = 0.0")
            print("  P(not Evacuees) = 1.0")
            print()
            return

        edge_ids = [int(p.split("_")[1]) for p in self.parents]
        q_fail_list = self.q_list


        k = len(edge_ids)
        for assignment in itertools.product([False, True], repeat=k):
            cond_parts = []
            for eid, val in zip(edge_ids, assignment):
                cond_parts.append(("flooded " if val else "not flooded ") + str(eid))
            cond_str = ", ".join(cond_parts)

            p_false = 1.0
            for val, qf in zip(assignment, self.q_list):
                if val:
                    p_false *= qf
            p_true = 1.0 - p_false

            print(f"  P(Evacuees|{cond_str}) = {p_true}")

        print()

    def p_given_parents(self, y_value, e):

        # WEATHER root
        if self.name == "W":
            return float(self.cpt[y_value])  # cpt["mild"]=0.1 etc.

        # FLOOD node: F_i with parent W
        if self.name.startswith("F_"):
            w = e["W"]
            return float(self.cpt[w][y_value])

        # EV node: noisy-or with failure q (compact)
        if self.name.startswith("Ev_"):
            prod_fail = 1.0
            for parent_name, qf in zip(self.parents, self.q_list):
                if e[parent_name] is True:  # flooded cause present
                    prod_fail *= float(qf)  # multiply failures
            p_false = prod_fail
            p_true = 1.0 - p_false
            return p_true if y_value is True else p_false

        raise Exception("Unknown node type")

    def values(self):
        return self.states