import math

class Node:

    def __init__(self, state, g, parent, action):
        self.state = state
        self.g = g
        self.parent = parent # parent is Node not a state
        self.action = action # action taken from parent to reach this node
        self.h = None
        self.f = None

    def compute_h(self, simulator):
        if self.h is None:
            self.h = self.state.mst_heuristic(simulator)
            self.f = self.g + self.h

    def expand(self, simulator):
        children = []
        successors = self.state.expand()

        for successor_state, action in successors:
            step_cost = simulator.step_cost(self.state._current_vertex,
                                            self.state._is_equipped, action)
            if math.isinf(step_cost):
                continue

            child = Node(successor_state, g=self.g+step_cost, parent=self, action=action)
            child.compute_h(simulator)
            children.append(child)

        return children