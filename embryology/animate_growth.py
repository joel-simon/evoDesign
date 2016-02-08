# import pickle, os, sys
# import pygame

# import time

# from visualize import draw_hex_map
# from simulate import simulate
# from hexmap import Map
# import experiments

# pygame.init()
# basicFont  = pygame.font.SysFont(None, 24)
# size   = width, height = 800, 800
# screen = pygame.display.set_mode(size)
# directory = 'temp_images/'

# def draw(hexmap, i):
# 	screen.fill((255,255,255))
# 	draw_hex_map(screen, hexmap, start = (0,0))
# 	pygame.display.flip()
# 	pygame.image.save(screen, directory + str(i)+'.jpg')
# 	time.sleep(.2)



# def main(args):
# 	genome = pickle.load(open(args.path, 'rb'), encoding='latin1')
# 	shape  = (args.rows, args.cols)

# 	if os.path.exists(directory):
# 		os.system("rm -rf "+directory)
# 	os.makedirs(directory)

# 	simulate(genome, shape, draw)
# 	time.sleep(.5)
# 	experiment = experiments.SurfaceArea(shape, screen).draw(genome)

# 	while True:
# 		for event in pygame.event.get():
# 			if event.type == pygame.QUIT:
# 				sys.exit()

# if __name__ == '__main__':
# 	import argparse
# 	parser = argparse.ArgumentParser()
# 	parser.add_argument('path', type=str)
# 	parser.add_argument('rows', type=int, nargs='?', default=8)
# 	parser.add_argument('cols', type=int, nargs='?', default=8)

# 	main(parser.parse_args())