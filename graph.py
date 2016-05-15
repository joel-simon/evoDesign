class Node(object):
  """docstring for Node"""
  def __init__(self, id, p, m = 10.0):
    self.id = id
    self.p = p
    self.m = m
    self.v = Vector(0,0)
    self.a = Vector(0,0)
    self.r = 16.0
    self.static = False

class Graph(object):
  """docstring for Graph"""
  def __init__(self):
    self.nodes = dict()
    self.node_set = dict()
    # self.edges = []

    # Node id -> set of adjacencie
    self.adjacencies = defaultdict(set)

    self.nextNodeId = 0
    self.nextEdgeId = 0

  def add_node(self, p, static=False):
    node = Node(self.nextNodeId, p)
    node.static = static
    self.nodes[node.id] = node
    self.node_set[node.id] = node
    self.nextNodeId += 1
    return node

  def add_edge(self, node1_id, node2_id):
    id_a = min(node1_id, node2_id)
    id_b = max(node1_id, node2_id)
    self.adjacencies[id_a].add(id_b)
    self.adjacencies[id_b].add(id_a)

  def add_edges(self, array):
    for (a,b) in array:
      self.add_edge(a, b)

  def clear_edges(self):
    self.adjacencies = defaultdict(set)

  def remove_node(self, node_id):
    for adjacency_node_id in self.adjacencies[node_id]:
      self.adjacencies[adjacency_node_id].remove(node_id)

    del self.adjacencies[node_id]

  def edges(self):
    for id1, neighbors in self.adjacencies.items():
      for id2 in neighbors:
        if id1 < id2:
          yield (self.nodes[id1], self.nodes[id2])

  def neighbors(self, node):
    for n_id in self.adjacencies[node.id]:
      yield self.nodes[n_id]