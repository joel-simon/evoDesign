

# def pca(X):
#   n_samples, n_features = X.shape
#   X -= np.mean(X, axis=0)
#   U, S, V = np.linalg.svd(X, full_matrices=False)
#   explained_variance_ = (S ** 2) / n_samples
#   explained_variance_ratio_ = (explained_variance_ /
#                                explained_variance_.sum())
#   return (V, explained_variance_ratio_)

# GREEN = (0,200,0)
# RED   = (200,0,0)
# BLUE  = (0,0,200)

# def fully_connected_draw(sim):
#   nodes = sim.physics.nodes
#   import time

#   for node in nodes:
#     assert(isinstance(node, Cell))
#     assert(node in sim.physics.adjacencies)

#   for node_a, neighbors in sim.physics.adjacencies.items():
#     for node_b in neighbors:
#       assert(node_a in sim.physics.adjacencies[node_b])

#   visited = set()
#   stack = set(nodes[:1])

#   while len(stack):
#     node = stack.pop()
#     assert(node not in stack)
#     node.color = RED
#     plot(nodes, sim.physics.edges())
#     time.sleep(1)

#     if node not in visited:
#       visited.add(node)
#       node.color = GREEN
#       plot(nodes, sim.physics.edges())
#       time.sleep(1)
#       neighbors = sim.physics.neighbors(node)
#       stack.update(neighbors.difference(visited))
#       assert(node not in stack)
#       for node in stack:
#         node.color = BLUE
#       plot(nodes, sim.physics.edges())
#       time.sleep(1)

#   if len(visited) != len(nodes):
#     time.sleep(1000)
#   return len(visited) == len(nodes)

# def fully_connected(sim):
#   nodes = sim.physics.nodes
#   visited = set()
#   stack = set(nodes[:1])

#   while len(stack):
#     node = stack.pop()
#     if node not in visited:
#       visited.add(node)
#       neighbors = sim.physics.neighbors(node)
#       stack.update(neighbors.difference(visited))
#       assert(node not in stack)

#   # print(len(visited), len(nodes))
#   return len(visited) == len(nodes)

# def score2(sim):
#   n = len(sim.physics.nodes)

#   if n < 10:
#     return 0

#   if not fully_connected(sim):
#     print('not fully_connected')
#     # fully_connected_draw(sim)
#     return 0

#   points = np.array([(n.px, n.py) for n in sim.physics.nodes])
#   _, variance = pca(points)
#   shape_score = variance[0]
#   return shape_score


# def evaluate_genome(genome, n_avgs=5):
#   fitnesses = []
#   for i in range(n_avgs):
#     physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=400.0,
#                                 damping=0.5, timestep = .03)
#     sim = Simulation(genome, physics, simulation_dimensions)
#     try:
#       sim.run(75)
#       fitnesses.append(score(sim))
#     except OverflowError:
#       fitnesses.append(0)
#     sim.reset()

#   return sum(fitnesses)/float(n_avgs)
