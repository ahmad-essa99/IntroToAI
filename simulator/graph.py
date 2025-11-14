from edge import Edge
from vertex import Vertex


class Graph:
    def __init__(self):
        self._vertices = {} # dict of int:Vertex
        self._edges = {}  # dict of int:Edge
        self._adj = {} # dict of int:list[tuple(Edge, Vertex)]

    def add_vertex(self, vertex: Vertex):
        vid = vertex._id
        self._vertices[vid] = vertex
        if vid not in self._adj:
            self._adj[vid] = []

    def add_edge(self, edge: Edge):
        self._edges[edge._id] = edge
        self._adj[edge._v1].append((edge._id, edge._v2))
        self._adj[edge._v2].append((edge._id, edge._v1))

    def __repr__(self):

        return (f"Graph Vertices:\n{self._vertices.__repr__()}"
                f"\nGraph Edges:\n{self._edges.__repr__()}"
                f"\nGraph Adj:\n{self._adj.__repr__()}"
                )