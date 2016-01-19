import pygame
import pygame.gfxdraw
import numpy as np

BLACK = (0,0,0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

def xy(screen, coords):
	w, h = screen.get_size()
	scale = 20
	margin = 5
	return (margin + int(scale * coords[0]),  h - int(scale *coords[1]) - margin )

def draw_truss(screen, truss, fitness=None, fos=None):
	basicFont = pygame.font.SysFont(None, 36)
	screen.fill((255,255,255))
	for m in truss.members:
		a_xy = xy(screen, m.joints[0].coordinates)
		b_xy = xy(screen, m.joints[1].coordinates)
		# if m.fos_yielding > 1:
		color = (100,100,100)
		# else:
		# 	color = ( int((1 - m.fos_yielding) * 255), int(m.fos_yielding * 255), 0)
		pygame.gfxdraw.line(screen,a_xy[0], a_xy[1], b_xy[0],b_xy[1], color)

	for j_i, joint in enumerate(truss.joints):
		# if a joint
		if joint.translation.sum() == 3:
			pos = xy(screen, joint.coordinates)
			pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], 3, (10,10,10))
		elif np.absolute(joint.loads).sum() > 0:
			pos = xy(screen, joint.coordinates)
			pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], 3, (200,0,0))
	
	if fitness != None:
		string = "Fitness: " + str(fitness)
		text = basicFont.render(string, True, (10, 10, 10))
		textrect = text.get_rect()
		textrect.centerx = 200
		textrect.centery = 50
		screen.blit(text, textrect)	
	if fos != None:
		string = "FOS: " + str(fos)
		text = basicFont.render(string, True, (10, 10, 10))
		textrect = text.get_rect()
		textrect.centerx = 200
		textrect.centery = 30
		screen.blit(text, textrect)

	pygame.display.flip()
