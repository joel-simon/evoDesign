import numpy as np
import time
np.set_printoptions(precision = 1, linewidth=125, suppress=True)
# from draw import draw

pygame.init()
size = width, height = 640, 480
screen = pygame.display.set_mode(size)
basicFont = pygame.font.SysFont(None, 24)
BLACK = (0,0,0)
WHITE = (255, 255, 255)

d = [[]]
def get_nodes(X):
	nodes = list()
	for i, j in np.ndindex(X.shape):
		if X[i,j]:
			nodes.append((i,j))
	
	node_map = {n:i for i, n in enumerate(nodes)}
	return (nodes, node_map)

def get_reactions(X, nodes, node_map):
	reactions = []
	i = X.shape[0] - 1
	for j in range(X.shape[1]):
		if X[i, j]:
			reactions.append((node_map[(i, j)], 'y'))
	return reactions

def get_external(X, nodes, node_map):
	external = np.zeros([len(nodes) *2])
	for i in node_map.values():
		external[2*i+1] = 1
	# external[3] = 10
	# external[0] = 1000
	return external

def xy(P, i, j):
	padding  = 5
	size = 100
	x = j*size + padding
	y = height - (P.shape[0] - i -1)*size - padding
	return (x, y)

def draw(P, nodes, edges, forces):
	forces = np.around(forces)
	screen.fill((255,255,255))
	padding = 5
	for i, j in np.ndindex(P.shape):
		if P[i, j]:
			pygame.draw.circle(screen, BLACK, xy(P, i, j), 2)
			text = basicFont.render(str(nodes.index((i,j))), True, (0, 0, 0), (255, 255, 255))
			textrect = text.get_rect()
			textrect.centerx = xy(P, i, j)[0]+10
			textrect.centery = xy(P, i, j)[1]
			screen.blit(text, textrect)

	for ((a, b), force) in zip(edges, forces):
		text = basicFont.render(str(force), True, (255, 0, 0), (255, 255, 255))
		a_xy = xy(P, *nodes[a])
		b_xy = xy(P, *nodes[b])

		textrect = text.get_rect()
		textrect.centerx = (b_xy[0] + a_xy[0])/2
		textrect.centery = (b_xy[1] + a_xy[1])/2
		screen.blit(text, textrect)

		pygame.draw.line(screen, (0,0,0), a_xy, b_xy, 1)

	pygame.display.flip()

def solve(nodes, edges, reactions, external):
	geo_matrix = np.zeros([ 2 * len(nodes), 2 * len(nodes) ])

	for e_i, (node_a_i, node_b_i) in enumerate(edges):
		node_a_y, node_a_x = nodes[node_a_i]
		node_b_y, node_b_x = nodes[node_b_i]
		a = np.array([node_a_x, node_a_y])
		b = np.array([node_b_x, node_b_y])

		angle = math.atan2((node_b_y-node_a_y),(node_b_x-node_a_x))
		h = math.cos(angle)
		v = math.sin(angle)

		geo_matrix[2*node_a_i, e_i] = h
		geo_matrix[2*node_b_i, e_i] = -h

		geo_matrix[2*node_a_i+1, e_i] = v
		geo_matrix[2*node_b_i+1, e_i] = -v


	for r_i, (node_i, direction) in enumerate(reactions):
		i = 2*node_i if direction == 'x' else 2*node_i +1
		geo_matrix[i, (r_i + len(edges))] = 1

	# print(geo_matrix)
	x, _, _, _ = np.linalg.lstsq(geo_matrix, external)
	return x

def main():
	l = 10
	X = np.array([[0, 0, 0, 0, 0],
								[0, 0, 0, 0, 0],
								[1, 0, 0, 0, 0],
								[1, 1, 0, 0, 0],
								[1, 1, 0, 0, 0]])
	# X = np.random.randint(2, size=(l,l))
	
	P = np.zeros([X.shape[0]+1, X.shape[1]+1], dtype='uint8')
	edges = []
	for i, j in np.ndindex(X.shape):
		if X[i, j]:
			edges.append(((i,j), (i+1, j+1)))
			# edges.append(((i+1,j), (i, j+1)))
			edges.append(((i,j), (i+1, j)))
			edges.append(((i,j), (i, j+1)))
			edges.append(((i+1,j), (i+1, j+1)))
			edges.append(((i,j+1), (i+1, j+1)))
			P[i:i+2, j:j+2] = 1

	nodes, node_map = get_nodes(P)
	edges = list(set(edges)) #remove duplicates
	edges = [(node_map[a], node_map[b]) for (a, b) in edges]
	reactions       = get_reactions(P, nodes, node_map)
	external        = get_external(P, nodes, node_map)

	reactions.append((15,'x'))

	print('nodes:     ', len(nodes))
	print('edges:     ', len(edges))
	print('reactions: ', len(reactions))
	print('external:  ', external)
	print()

	if 2*len(nodes) < len(edges)+len(reactions):
		return print('indeterminate!', 2*len(nodes), len(edges)+len(reactions))

	forces = solve(nodes, edges, reactions, external)
	print('forces:', forces)
	draw(P, nodes, edges, forces)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			time.sleep(20)
main()
# print x
# print forces_per_node
# force_names = []
# for i, conn in enumerate(connections):
	# d = 'x' if (i%2 == 0) else 'y'
	# force_names.append(str(i/2)+str(d))
# print force_names/
# print x

	# forces_per_node = np.zeros([len(nodes) * 2])
	# forces_per_node = [[] for _ in range(len(nodes) * 2)]

	# for c_i, (a_i, b_i) in enumerate(edges):
	# 	force = x[c_i]
	# 	forces_per_node[2*a_i+1].append(-force)
	# 	forces_per_node[2*b_i+1].append(force)

	# for f_i, force in enumerate(external):
	# 	if force != 0:
	# 		forces_per_node[f_i].append(force)

	# for r_i, (n_i, direction) in enumerate(reactions):
	# 	force = x[r_i + len(edges)]
	# 	forces_per_node[2*n_i+1].append(-force)