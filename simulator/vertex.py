
class Vertex:

    def __init__(self, id: int, num_of_people: int = 0):
        self._id = id
        self._num_of_people = num_of_people

    def __repr__(self):
        return (f"Vertex(id={self._id}:,"
                f" num_of_people={self._num_of_people})")