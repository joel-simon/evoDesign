# Basic OBJ file viewer. needs objloader from:
#  http://www.pygame.org/wiki/OBJFileLoader
# LMB + move: rotate
# RMB + move: pan
# Scroll wheel: zoom in/out
import sys, pygame
from pygame.locals import *
from pygame.constants import *
from OpenGL.GL import *
from OpenGL.GLU import *

from primitive import make_plane, G_OBJ_PLANE
import numpy as np

class Viewer(object):
    def __init__(self, bounds):
        self.bounds = bounds
        pygame.init()

        viewport = (800,600)
        hx = viewport[0]/2
        hy = viewport[1]/2
        srf = pygame.display.set_mode(viewport, OPENGL | DOUBLEBUF)

        glLightfv(GL_LIGHT0, GL_POSITION,  (-40, 200, 100, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHTING)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.4, 0.4, 0.4, 0.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = viewport
        gluPerspective(90.0, width/float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

        glTranslated(-15, -15, -15)
        make_plane(*self.bounds)

        self.nodes = [(.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5),
                     (-.5, -.5, -.5),(.5, -.5, .5), (.5, .5, .5),
                     (-.5, -.5, .5), (-.5, .5, .5) ]
        self.edges = [(0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),
                      (5,1),(5,4),(5,7)]

        self.rx, self.ry = (0,0)
        self.tx, self.ty = (0,0)
        self.zpos = 10

        self.gl_list = None
        # self.font = pygame.font.SysFont("monospace", 64)

    # def drawText(self, position, textString):

    #     textSurface = self.font.render(textString, True, (255,255,255,255), (0,0,0,255))
    #     textData = pygame.image.tostring(textSurface, "RGBA", True)
    #     glRasterPos2d(*position)
    #     glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

    # def 

    def add_mesh(self, nodes, edges, colors):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)
        glLineWidth(3)
        glBegin(GL_LINES)
        glColor3f(0, 0, 0)
        for (i, j), color in zip(edges, colors):
            glColor3fv(color)
            glVertex3fv(nodes[i])
            glVertex3fv(nodes[j])
        glEnd()
        glLineWidth(1)
        glEndList()


    def set_map(self, hmap):
        return
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

        for x, y, z in zip(*np.where(hmap)):
            if hmap[x][y][z].userData['connected']:
                self.draw_cube(x, y, z)
            else:
                self.draw_cube(x, y, z, (.5, .5, .5))

        glEndList()

    def draw_cube(self, x, y, z, color=(100, 100, 100)):
        vertices = np.array([[.5, -.5, -.5], [.5, .5, -.5], [-.5, .5, -.5],
                     [-.5, -.5, -.5],[.5, -.5, .5], [.5, .5, .5],
                     [-.5, -.5, .5], [-.5, .5, .5] ]) + np.array([x, y, z])

        edges = [(0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),
                 (5,1),(5,4),(5,7)]

        normals = [(-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0)]

        glLineWidth(3)
        glBegin(GL_LINES)

        glColor3f(0, 0, 0)

        for i, j in self.edges:
            glVertex3fv(vertices[i])
            glVertex3fv(vertices[j])

        glEnd()
        glLineWidth(1)

        vertices = np.array([((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
            ((-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)),
            ((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)),
            ((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
            ((-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
            ((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5))])*.99 + np.array([x, y, z])
        normals = [(-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0)]

        glColor3fv(color)
        glBegin(GL_QUADS)
        for i in xrange(6):
            glNormal3f(normals[i][0], normals[i][1], normals[i][2])
            for j in xrange(4):
                glVertex3f(vertices[i][j][0], vertices[i][j][1], vertices[i][j][2])
        glEnd()

    def main_loop(self):
        rotate = move = False
        while 1:
            self.clock.tick(30)
            for e in pygame.event.get():
                if e.type == QUIT:
                    # sys.exit()
                    return
                elif e.type == KEYDOWN and e.key == K_ESCAPE:
                    # sys.exit()
                    return
                elif e.type == MOUSEBUTTONDOWN:
                    if e.button == 4: self.zpos = max(1, self.zpos-1)
                    elif e.button == 5: self.zpos += 1
                    elif e.button == 1: rotate = True
                    elif e.button == 3: move = True
                elif e.type == MOUSEBUTTONUP:
                    if e.button == 1: rotate = False
                    elif e.button == 3: move = False
                elif e.type == MOUSEMOTION:
                    i, j = e.rel
                    if rotate:
                        self.rx += i
                        self.ry += j
                    if move:
                        self.tx += i
                        self.ty -= j
                # elif

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # RENDER OBJECT
            glTranslate(self.tx/20., self.ty/20., - self.zpos)
            glRotate(self.ry, 1, 0, 0)
            glRotate(self.rx, 0, 1, 0)

            if self.gl_list:
                glCallList(self.gl_list)
            glCallList(G_OBJ_PLANE)
            # self.drawText((0,0), 'hello world')
            pygame.display.flip()
