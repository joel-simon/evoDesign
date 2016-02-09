import sys, time, math
import numpy as np
from collections import defaultdict
from trussme import truss
import warnings
SQRT3 = math.sqrt( 3 )

def derp(row, col, radius):
	offset = radius * SQRT3 / 2 if col % 2 else 0
	top = offset + SQRT3 * row * radius
	left = 1.5 * col * radius
	return (top, left)

def truss_from_map(hex_map, real_radius=1):
	radius = .75
	t1 = truss.Truss()

	hex_to_members = dict()

	nodes = defaultdict()
	nodes.default_factory = nodes.__len__
	members = set()
	hex_coords = [( .5 * radius, 0 ),
		( 1.5 * radius, 0 ),
		( 2 * radius, SQRT3 / 2 * radius ),
		( 1.5 * radius, SQRT3 * radius ),
		( .5 * radius, SQRT3 * radius ),
		( 0, SQRT3 / 2 * radius )
	]
	edges = [(0,1), (1,2), (2,3), (3,4), (4,5), (5,0), (0, 4), (0,3), (1,3)]
	
	max_y = derp(hex_map.rows - 1, 1, radius)[0] + (SQRT3 * radius)

	for col in range(hex_map.cols):
		
		for row in range(hex_map.rows):

			top, left = derp(row, col, radius)
			if hex_map.values[row][col] == 0:
				continue

			new_nodes = [( round(x + left, 2), round(y + top, 2)) for ( x, y ) in hex_coords]

			for ( x, y ) in new_nodes:
				nodes[(x, y)]

			for (i,j) in edges:
				if (new_nodes[j], new_nodes[i]) not in members:
					members.add((new_nodes[i], new_nodes[j]))

	# Add joints
	for ((x, y), n) in sorted(nodes.items(), key = lambda t: t[1]):
		if y == 0:
			t1.add_support(np.array([x, y, 0.0]), d=2)
		else:
			t1.add_joint(np.array([x, y, 0.0]), d=2)

	# Add members
	for m_a, m_b in members:
		t1.add_member(nodes[m_a], nodes[m_b])

	return t1
