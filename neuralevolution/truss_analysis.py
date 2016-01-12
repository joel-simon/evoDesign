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

def truss_from_map(hex_map, radius):
	t1    = truss.Truss()
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
	
	max_y = int(derp(hex_map.values.shape[0] - 1, 1, radius)[0] + (SQRT3 * radius))

	for col in range(hex_map.values.shape[1]):
		
		for row in range(hex_map.values.shape[0]):
			top, left = derp(row, col, radius)
			if hex_map.values[row, col] == 0:
				continue

			new_nodes = [( int(x + left), int(y + top)) for ( x, y ) in hex_coords]

			for ( x, y ) in new_nodes:
				nodes[(x, y)]

			for (i,j) in edges:
				if (new_nodes[j], new_nodes[i]) not in members:
					members.add((new_nodes[i], new_nodes[j]))

	# Add joints
	for ((x, y), n) in sorted(nodes.items(), key = lambda t: t[1]):
		if y == 0: #or y == int(SQRT3 / 2 * radius)
			t1.add_support(np.array([x, y, 0.0]), d=2)
		else:
			t1.add_joint(np.array([x, y, 0.0]), d=2)

	# Add members
	for m_a, m_b in members:
		t1.add_member(nodes[m_a], nodes[m_b])
		# t1.members[-1].set_shape('bar', update_props=True)
		t1.members[-1].set_parameters(t=0.25, r=1, update_props=True)

	# Add Forces
	x_force = 3000
	y_force = -10
	
	for joint in t1.joints:
		if joint.coordinates[1] == max_y:
			joint.loads[1] = y_force

		# joint.coordinates /= radius
	# max_y
	# for i, j in np.ndindex(mask.shape):
	# 	# x force
	# 	if mask[i, j] == 2:
	# 		if (i,j+1) in nodes:
	# 			t1.joints[nodes[(i,j+1)]].loads[0] = x_force
	# 	# y force
	# 	elif mask[i, j] == 3:
	# 		if (i,j) in nodes:
	# 			t1.joints[nodes[(i,j)]].loads[1] = y_force

	return t1
