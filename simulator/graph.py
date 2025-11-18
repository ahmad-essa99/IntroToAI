from edge import Edge
from vertex import Vertex
import math
import heapq


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

    def get_edge(self, vertex1, vertex2):
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


    def print_vertex_info(self, vertex_id):
        vertex = self._vertices[vertex_id]
        print(f"Current Vertex ({vertex_id}) Info")
        print(f"People here    : {vertex._num_of_people}")
        print(f"Kits here      : {vertex._num_of_kits}")
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

    def _shortest_path_with_simple_dijkstra(self, source_vertex, agent_is_equipped):
        dist = {}
        prev = {}

        for vertex_id in self._vertices.keys():
            dist[vertex_id] = math.inf
            prev[vertex_id] = None

        dist[source_vertex] = 0
        heap = [(0, source_vertex)]

        while heap:
            current_vertex_val, current_vertex = heapq.heappop(heap)
            if current_vertex_val != dist[current_vertex]:
                continue  # current entry is not relevant

            neighbors = self._adj.get(current_vertex)

            for (edge_id, neighbor_id) in neighbors:
                edge = self._edges[edge_id]

                if edge._is_flooded and not agent_is_equipped:
                    continue

                w = edge._weight
                neighbor_new_val = current_vertex_val + w

                if neighbor_new_val < dist[neighbor_id]:
                    dist[neighbor_id] = neighbor_new_val
                    prev[neighbor_id] = current_vertex
                    heapq.heappush(heap, (neighbor_new_val, neighbor_id))

        return dist, prev

    def _reconstruct_path(self, prev, source_id, target_id):

        path = []
        current = target_id
        while current is not None and current != source_id:
            path.append(current)
            current = prev[current]

        if current is None:
            return []

        path.reverse()
        return path