
class Edge:
    def __init__(self, id: int, v1: int, v2: int, weight: int,
                 flooded_prob_given_mild: float = 0.0):

        self._id = id
        self._v1 = v1
        self._v2 = v2
        self._weight = weight
        self._flooded_prob_given_mild = float(flooded_prob_given_mild)
        self._flooded_prob_given_stormy = min(1.0, self._flooded_prob_given_mild*2.0)
        self._flooded_prob_given_extreme = min(1.0, self._flooded_prob_given_mild*3.0)

        if self._flooded_prob_given_mild < 0.0 or self._flooded_prob_given_mild > 1.0:
            raise Exception(f"Edge {self._id} flooded prob given mild value Error: {self._flooded_prob_given_mild}")

        if self._flooded_prob_given_stormy < 0.0 or self._flooded_prob_given_stormy > 1.0:
            raise Exception(f"Edge {self._id} flooded prob given stormy value Error: {self._flooded_prob_given_stormy}")

        if self._flooded_prob_given_extreme < 0.0 or self._flooded_prob_given_extreme > 1.0:
            raise Exception(f"Edge {self._id} flooded prob given extreme value Error: {self._flooded_prob_given_extreme}")



    def __repr__(self):
        return (f"Edge(id={self._id},"
                f" [V{self._v1} - V{self._v2}],"
                f" weight={self._weight}")