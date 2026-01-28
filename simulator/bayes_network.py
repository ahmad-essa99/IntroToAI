class BayesNetwork:
    def __init__(self):
        self.nodes = {}  # name -> BNNode

    def add_node(self, node):
        if node.name in self.nodes:
            raise Exception(f"Duplicate BN node name: {node.name}")
        self.nodes[node.name] = node

    def get_node(self, name):
        return self.nodes[name]

    def print_network(self):
        # 1) WEATHER
        if "W" in self.nodes:
            self.nodes["W"].print()

        edge_nodes = []
        for name, node in self.nodes.items():
            if name.startswith("F_"):
                eid = int(name.split("_")[1])
                edge_nodes.append((eid, node))

        edge_nodes.sort(key=lambda x: x[0])

        for _, node in edge_nodes:
            node.print()

        vertex_nodes = []
        for name, node in self.nodes.items():
            if name.startswith("Ev_"):
                vid = int(name.split("_")[1])
                vertex_nodes.append((vid, node))

        vertex_nodes.sort(key=lambda x: x[0])

        for _, node in vertex_nodes:
            node.print()

    def vars_in_order(self, query, evidence):
        W = ["W"] if "W" in self.nodes else []
        Fs = sorted([n for n in self.nodes if n.startswith("F_")],
                    key=lambda s: int(s.split("_")[1]))
        Evs = sorted([n for n in self.nodes if n.startswith("Ev_") and (n == query or n in evidence)],
                     key=lambda s: int(s.split("_")[1]))
        return W + Fs + Evs

    def enumeration_ask(self, X_name, evidence):
        Q = {}
        X = self.get_node(X_name)

        if X_name in evidence:
            x_obs = evidence[X_name]
            out = {x: 0.0 for x in X.states}
            out[x_obs] = 1.0
            return out


        for x in X.values():
            e2 = dict(evidence)
            e2[X_name] = x
            Q[x] = self.enumerate_all(self.vars_in_order(X_name, evidence), e2)
        # normalize
        s = sum(Q.values())

        out = {k: v / s for k, v in Q.items()}

        # ---- minimal "pretty" fix ----
        out = {k: round(v, 6) for k, v in out.items()}

        return out

    def enumerate_all(self, vars_list, e):
        if not vars_list:
            return 1.0

        Y_name = vars_list[0]
        Y = self.get_node(Y_name)

        if Y_name in e:
            return Y.p_given_parents(e[Y_name], e) * self.enumerate_all(vars_list[1:], e)
        else:
            total = 0.0
            for y in Y.values():
                e2 = dict(e)
                e2[Y_name] = y
                total += Y.p_given_parents(y, e2) * self.enumerate_all(vars_list[1:], e2)
            return total

    def report_posteriors(self, evidence: dict):

        print("=== Current Evidence ===")
        print(f"  {evidence}")
        print()



        print("=== Weather distribution (given evidence) ===")
        w_post = self.enumeration_ask("W", evidence)
        print(f"  P(mild)    = {w_post['mild']:g}")
        print(f"  P(stormy)  = {w_post['stormy']:g}")
        print(f"  P(extreme) = {w_post['extreme']:g}")
        print()

        # 2) Edges flooded probabilities
        print("=== Edge flooding probabilities (given evidence) ===")
        edge_nodes = sorted(
            [name for name in self.nodes if name.startswith("F_")],
            key=lambda s: int(s.split("_")[1])
        )
        for fname in edge_nodes:
            post = self.enumeration_ask(fname, evidence)
            print(f"  P({fname}=True) = {post[True]:g}")
        print()

        # 1) Vertex evacuees probabilities
        print("=== Vertex evacuees probabilities (given evidence) ===")
        ev_nodes = sorted(
            [name for name in self.nodes if name.startswith("Ev_")],
            key=lambda s: int(s.split("_")[1])
        )
        for evname in ev_nodes:
            post = self.enumeration_ask(evname, evidence)  # {False:..., True:...}
            print(f"  P({evname}=True) = {post[True]:g}")
        print()

    def probability_path_free(self, path_edge_ids, evidence):

        mechany = self.enumerate_all(self.vars_in_order(None, evidence), dict(evidence))
        if mechany == 0.0:
            raise ValueError("Evidence inconsistent (P(evidence)=0)")

        e2 = dict(evidence)
        for eid in path_edge_ids:
            key = f"F_{eid}"
            if key in e2 and e2[key] is True:
                return 0.0
            e2[key] = False

        mone = self.enumerate_all(self.vars_in_order(None, e2), e2)

        return round(mone / mechany, 6)


