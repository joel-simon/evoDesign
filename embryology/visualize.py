import pygame
import pygame.gfxdraw
import numpy as np
import math

BLACK = (0,0,0)
GREY  = (50, 50, 50)
WHITE = (255, 255, 255)
RED   = (200, 0, 0)
GREEN = (0, 200, 0)
SQRT3 = math.sqrt( 3 )

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


def derp(row, col, radius):

	return (top, left)

def hex_points(row, col, radius, screen_height):
	offset = radius * SQRT3 / 2 if col % 2 else 0
	top    = offset + SQRT3 * row * radius
	left    = 1.5 * col * radius

	hex_coords = [( .5 * radius, 0 ),
		( 1.5 * radius, 0 ),
		( 2 * radius, SQRT3 / 2 * radius ),
		( 1.5 * radius, SQRT3 * radius ),
		( .5 * radius, SQRT3 * radius ),
		( 0, SQRT3 / 2 * radius ),
		( .5 * radius, 0 )
	]
	return [((x + left), ( y + top)) for ( x, y ) in hex_coords]

def draw_hex_map(screen, hexmap, start = (0,0)):
	radius = 30
	margin = 3
	w, h = screen.get_size()
	for col in range(hexmap.values.shape[1]):
		for row in range(hexmap.values.shape[0]):
			
			points = hex_points(row, col, radius, h)
			for i, (x, y) in enumerate(points):
				points[i] = (x+margin+start[0], h-y-margin)
			# pygame.gfxdraw.aapolygon(screen, points, BLACK)
			if hexmap.values[row, col] != 0.0:
				pygame.draw.polygon(screen, GREEN, points)
			pygame.draw.polygon(screen, GREY, points, 1)
	return

if __name__ == '__main__':
	from hexmap import Map
	
	a = Map((8, 8))
	a.values += 1
	
	pygame.init()
	screen = pygame.display.set_mode((800, 500))
	screen.fill((255,255,255))
	draw_hex_map(screen, a)
	pygame.display.flip()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit()