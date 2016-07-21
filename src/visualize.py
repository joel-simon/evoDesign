# from scipy.spatial import Voronoi
# import time
# import pygame
# import pygame.gfxdraw
# pygame.init()
# font = pygame.font.SysFont("monospace", 18)
# screen = pygame.display.set_mode((800, 800))

# # from box2DPhysics import Box2DPhysics
# # from physics import VoronoiSpringPhysics
# from os.path import join
# import sys
# import os
# import subprocess
# import argparse

# BLACK = (0,0,0)
# LIGHT_GREEN = (0, 200, 0, 10)

# import numpy as np

# def pca(X):
#   n_samples, n_features = X.shape
#   X -= np.mean(X, axis=0)
#   U, S, V = np.linalg.svd(X, full_matrices=False)
#   explained_variance_ = (S ** 2) / n_samples
#   explained_variance_ratio_ = (explained_variance_ /
#                                explained_variance_.sum())
#   return (V, explained_variance_ratio_)

# def render(physics):
#   # print(render)
#   edges = physics.edges()
#   bodies = physics.bodies

#   map_pos = lambda p: (int(p[0])+400, int(p[1]) + 400)
#   points = [n.position for n in bodies]

#   # print(len(bod) points)
#   # points = [n.position for n in sim.cells]

#   screen.fill((255,255,255))

#   # c_a = [ n.morphogen_concentrations[0][0] for n in bodies ]
#   # c_b = [ n.morphogen_concentrations[0][1] for n in bodies ]

#   max_stress = max(n.get_stress() for n in bodies)

#   # m_range = (min(c_a), max(c_a))

#   # mintext = font.render("a range:(%f, %f)" % (min(c_a), max(c_a)),1,(0,0,0) )
#   # screen.blit(mintext, (10,10))

#   # mintext = font.render("b range:(%f, %f)" % (min(c_b), max(c_b)),1,(0,0,0) )
#   # screen.blit(mintext, (10,30))

#   num_bodies = font.render("# bodies: %i" % len(bodies),1,(0,0,0) )
#   screen.blit(num_bodies, (10,50))

#   for body in bodies:
#     x, y = map_pos(body.position)
#     pygame.gfxdraw.aacircle(screen, x, y, int(body.r), (10, 10, 10))

#     # a = node.morphogen_concentrations[0][0]
#     # red = int(200 * (a-m_range[0])/(1+m_range[1]-m_range[0]))
#     # pygame.gfxdraw.filled_circle(screen, x, y, int(node.r), (200, 10, 10, red))

#   for (bodyA, bodyB) in edges:
#     x1, y1 = map_pos(bodyA.position)
#     x2, y2 = map_pos(bodyB.position)
#     pygame.gfxdraw.line(screen, x1, y1, x2, y2, (10, 10, 10, 100))

#   # V, variance = pca(np.array(points))
#   # v = V[0]
#   # x1, y1, = 400,400
#   # x2 = int(400+50*v[0])
#   # y2 = 800 - int(400+50*v[1])
#   # pygame.draw.line(screen, (10,10,10), (x1, y1), (x2, y2), 5)

#   # vor = Voronoi(points)
#   # verts = vor.vertices
#   # for ii, region in enumerate(vor.regions):
#   #   if len(region) > 2 and -1 not in region:
#   #     pointlist = [map_pos(verts[i]) for i in region]
#   #     pygame.gfxdraw.aapolygon(screen, pointlist, (10,10,10))
#   #   elif -1 in region and ii < 20:
#   #     point = points[ii]
#   #     x, y = map_pos(point)
#   #     pygame.gfxdraw.filled_circle(screen, x, y, 4, (255,10,10))

#   pygame.display.flip()
#   # time.sleep(1)

# # class VisualVoronoiSpringPhysics(VoronoiSpringPhysics):
# #   """docstring for VisualVoronoiSpringPhysics"""
# #   def __init__(self, save=False, *args, **kwargs):
# #     self.save = save
# #     self.frame = 0

# #     os.system("rm -rf temp")
# #     os.makedirs('temp')

# #     super(VisualVoronoiSpringPhysics, self).__init__(*args, **kwargs)

#   # def step(self):
#   #   super(VisualVoronoiSpringPhysics, self).step()
#   #   plot(self.bodies, self.edges())
#   #   if self.save:
#   #     pygame.image.save(screen, "temp/%i.jpg" % self.frame)
#   #     self.frame += 1

# # class VisualBox2DPhysics(Box2DPhysics):
# #   """docstring for VisualVoronoiSpringPhysics"""
# #   def __init__(self, save=False, *args, **kwargs):
# #     self.frame = 0

# #     super(VisualBox2DPhysics, self).__init__(*args, **kwargs)

# #   def step(self):
# #     super(VisualBox2DPhysics, self).step()
# #     # plot(self.world.bodies, self.edges())

# def main(args):
#   import pickle
#   import sys
#   import random
#   from simulation import Simulation
#   path = args.dir

#   # with open(join(path, 'population.p'), 'rb') as f:
#   #   pop = pickle.load(f)#, encoding='latin1')

#   with open(join(path, 'genome.p'), 'rb') as f:
#     best_genome = pickle.load(f)#, encoding='latin1')

#   video_path = join(path, 'animation.avi')
#   save = args.save

#   physics = VoronoiSpringPhysics(stiffness=400.0, repulsion=600.0,
#                                         damping=0.5, timestep = .03, save=save)

#   # best_genome = pop.statistics.best_genome()
#   sim = Simulation(best_genome, physics, (800, 800), render=plot, verbose=True)

#   sim.run(80)
#   print('run over')

#   if save:
#     subprocess.call(['avconv','-i','temp/%d.jpg','-r','12',
#                     '-threads','auto','-qscale','1','-s','800x800', video_path])
#     os.system("rm -rf temp")
#     print('Created video file.')

#   while True:
#     for event in pygame.event.get():
#       if event.type == pygame.QUIT:
#         sys.exit()

# def main():
#   import pickle
#   import sys
#   import random
#   from simulation import Simulation
#   path = args.dir

# if __name__ == '__main__':
#   parser = argparse.ArgumentParser()
#   parser.add_argument('dir', help='Input directory')
#   parser.add_argument('--save')
#   args = parser.parse_args()
#   main(args)
