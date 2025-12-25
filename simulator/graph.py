from edge import Edge
from vertex import Vertex
import math
import heapq


class Graph:
    def __init__(self):
        self._vertices = {} # dict of int:Vertex
        self._edges = {}  # dict of int:Edge
        self._adj = {} # dict of int:list[tuple(Edge, Vertex)]


    def get_target_vertices(self):
        target_vertices = {}
        for _,vertex in self._vertices.items():
            if vertex._num_of_people > 0:
                target_vertices[vertex._id] = vertex._num_of_people

        return target_vertices

    def add_vertex(self, vertex: Vertex):
        vid = vertex._id
        self._vertices[vid] = vertex
        if vid not in self._adj:
            self._adj[vid] = []

    def add_edge(self, edge: Edge):
        self._edges[edge._id] = edge
        self._adj[edge._v1].append((edge._id, edge._v2))
        self._adj[edge._v2].append((edge._id, edge._v1))

    def get_edge(self, vertex1: int, vertex2: int) -> Edge:
        edge_id = None

        for current_edge_id,neighbor_id in self._adj[vertex1]:
            if neighbor_id == vertex2:
                edge_id = current_edge_id
                break

        return self._edges[edge_id]

    def is_connected(self, vertex1, vertex2):
        for _,neighbor_id in self._adj[vertex1]:
            if neighbor_id == vertex2:
                return True

        return False

    def expand(self, vertex_id, is_equipped):

        assert (vertex_id in self._vertices.keys()
                and vertex_id in self._adj.keys()), f"can't expand {vertex_id}, it is not a vertex id"
        ret = []
        for edge_id, neighbor_id in self._adj[vertex_id]:
            if is_equipped or not self._edges[edge_id]._is_flooded:
                ret.append(neighbor_id)
        return ret

    def print_vertex_info(self, vertex_id, kits_in_vertex, debug=True):
        if debug:
            vertex = self._vertices[vertex_id]
            print(f"Current Vertex ({vertex_id}) Info")
            print(f"People here    : {vertex._num_of_people}")
            print(f"Kits here      : {kits_in_vertex}")
            print()

            print("Neighbors:")
            for (edge_id, neighbor_id) in self._adj[vertex_id]:
                edge = self._edges[edge_id]
                flood = "FLOODED" if edge._is_flooded else "Not FLOODED"
                print(f"  -> Vertex {neighbor_id} via Edge {edge_id} (weight {edge._weight}, {flood})")

            print("----------------------------------------------")

    def __repr__(self):

        return (f"Graph Vertices:\n{self._vertices.__repr__()}"
                f"\nGraph Edges:\n{self._edges.__repr__()}"
                f"\nGraph Adj:\n{self._adj.__repr__()}"
                )



