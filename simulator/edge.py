
class Edge:
    def __init__(self, id: int, v1: int, v2: int, weight: int,
                 is_flooded: bool = False):

        self._id = id
        self._v1 = v1
        self._v2 = v2
        self._weight = weight
        self._is_flooded = is_flooded


    def __repr__(self):
        return (f"Edge(id={self._id},"
                f" [V{self._v1} - V{self._v2}],"
                f" weight={self._weight},"
                f" is_flooded={self._is_flooded})")