import pygame
import numpy as np

BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
def xy(screen, coords):
	w, h = screen.get_size()
	return (int(coords[0]), h - int(coords[1]))

def draw_truss(screen, truss, radius):
	
	screen.fill((255,255,255))
	for m in truss.members:
		a_xy = xy(screen, m.joints[0].coordinates)
		b_xy = xy(screen, m.joints[1].coordinates)
		# if m.fos_yielding > 1:
		color = (0, 255, 0)
		# else:
		# 	color = ( int((1 - m.fos_yielding) * 255), int(m.fos_yielding * 255), 0)
		pygame.draw.line(screen, color, a_xy, b_xy, 2)

	for j_i, joint in enumerate(truss.joints):
		# if a joint
		if joint.translation.sum() == 3:
			pygame.draw.circle(screen, BLACK, xy(screen, joint.coordinates), 4)
		elif np.absolute(joint.loads.sum()) > 0:
			pygame.draw.circle(screen, RED, xy(screen, joint.coordinates), 4)

	pygame.display.flip()