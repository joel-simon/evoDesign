import pygame
import pygame.gfxdraw
import numpy as np
import math

from simulate import simulate
import os, sys
from images2gif import writeGif
import gzip
import pickle
from PIL import Image
import time
from shutil import copyfile


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

from neat import nn, ctrnn
def draw_hex_map(screen, hexmap, start = (0,0)):
	radius = 20
	margin = 3
	w, h = screen.get_size()
	for col in range(hexmap.cols):
		for row in range(hexmap.rows):
			cell = hexmap.values[row][col]

			points = hex_points(row, col, radius, h)
			for i, (x, y) in enumerate(points):
				points[i] = (x+margin+start[0], h-y-margin)

			if cell == -1:
				pygame.draw.polygon(screen, BLACK, points)

			elif isinstance(cell, ctrnn.Network):
				pygame.draw.polygon(screen, GREEN, points)

			pygame.draw.polygon(screen, GREY, points, 1)

	return

# def main(args):
def make_gif(screen, genome, experiment, filename):
	folder = 'temp_images/'
	if os.path.exists(folder):
		os.system("rm -rf "+folder)
	os.makedirs(folder)

	def gif_frame(hexmap, i):
		screen.fill((255,255,255))
		draw_hex_map(screen, hexmap, start = (0,0))
		pygame.display.flip()
		if filename:
			pygame.image.save(screen, folder + str(i)+'.jpg')
		else:
			time.sleep(.5)

	simulate(genome, experiment.shape, experiment.cell_inputs, gif_frame, experiment.start)
	experiment.draw(genome)

	if filename:
		n = len([fn for fn in os.listdir(folder) if fn.endswith('.jpg')])
		file_names = [folder+str(i)+'.jpg' for i in range(n)]
		images = [Image.open(fn) for fn in file_names]
		writeGif(filename+'.gif', images, duration=0.5)
		copyfile(folder+str(n-1)+'.jpg', './'+filename+'.jpg')

	else:
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
# if __name__ == '__main__':
# 	import argparse
# 	parser = argparse.ArgumentParser()
# 	parser.add_argument('path', type=str)
# 	parser.add_argument('rows', type=int, nargs='?', default=8)
# 	parser.add_argument('cols', type=int, nargs='?', default=8)

# 	main(parser.parse_args())

# 	while True:
# 		for event in pygame.event.get():
# 			if event.type == pygame.QUIT:
# 				sys.exit()
