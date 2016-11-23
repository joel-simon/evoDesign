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
from OpenGL.GLUT import *

from primitive import make_plane, G_OBJ_PLANE, make_sphere, G_OBJ_SPHERE
import numpy as np

class Viewer(object):
    def __init__(self, bounds):
        self.bounds = bounds
        pygame.init()
        glutInit()
        # viewport = (1200,800)
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

        # Transparancy?
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        self.clock = pygame.time.Clock()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        width, height = viewport
        gluPerspective(90.0, width/float(height), 1, 100.0)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)

        glTranslated(-15, -15, -15)
        make_plane(*self.bounds)

        self.rx, self.ry = (0,0)
        self.tx, self.ty = (0,0)
        self.zpos = 10

        self.gl_lists = []
        self.draw_grid = True
        # self.font = pygame.font.SysFont("monospace", 64)

    # def drawText(self, position, textString):

    #     textSurface = self.font.render(textString, True, (255,255,255,255), (0,0,0,255))
    #     textData = pygame.image.tostring(textSurface, "RGBA", True)
    #     glRasterPos2d(*position)
    #     glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

    # def
    def start_draw(self):
        self.gl_list = glGenLists(1)
        glNewList(self.gl_list, GL_COMPILE)

    def end_draw(self):
        assert(self.gl_list)
        glEndList()
        self.gl_lists.append(self.gl_list)
        self.gl_list = None

    def draw_arrow(self, p, v, s=.25, c = (0, 0, 0)):
        v = np.array(v)
        v_norm = np.linalg.norm(v)

        if v_norm == 0:
            raise ValueError('Invalid vector.')

        p2 = np.array(p) - (np.array(v) * s) / v_norm
        glLineWidth(3)
        glBegin(GL_LINES)
        glColor3fv(c)
        glVertex3fv(p)
        glVertex3fv(p2)
        glEnd()

    def draw_mesh(self, nodes, edges, colors, widths):
        for (i, j), color, width in zip(edges, colors, widths):
            glLineWidth(width)
            glBegin(GL_LINES)
            glColor3fv(color)
            glVertex3fv(nodes[i])
            glVertex3fv(nodes[j])
            glEnd()
        glLineWidth(1)

    def set_map(self, hmap):
        gl_list = glGenLists(1)
        glNewList(gl_list, GL_COMPILE)

        for x, y, z in zip(*np.where(hmap)):
            if hmap[x][y][z].userData['connected']:
                self.draw_cube(x, y, z, (.9, .9, .9, 1))
            else:
                self.draw_cube(x, y, z, (.5, .5, .5, .2), border=False)

        glEndList()
        self.gl_lists.append(gl_list)

    def foo(self, *args, **kwargs):
        self.start_draw()
        self.draw_cube(*args, **kwargs)
        self.end_draw()

    def draw_cube(self, x, y, z, color, border=True, scale=np.array([1,1,1])):
        if border:
            vertices = np.array([
                        [.5, -.5, -.5], [.5, .5, -.5], [-.5, .5, -.5],
                        [-.5, -.5, -.5],[.5, -.5, .5], [.5, .5, .5],
                        [-.5, -.5, .5], [-.5, .5, .5] ]) * scale + np.array([x, y, z])

            edges = [(0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),
                     (5,1),(5,4),(5,7)]

            glLineWidth(3)
            glBegin(GL_LINES)

            glColor3f(0, 0, 0)

            for i, j in edges:
                glVertex3fv(vertices[i])
                glVertex3fv(vertices[j])

            glEnd()
            glLineWidth(1)

        vertices = np.array([((-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
            ((-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)),
            ((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)),
            ((-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
            ((-0.5, -0.5, 0.5), (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
            ((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5))])*.99 * scale + np.array([x, y, z])
        # vertices = np.array([(3, 6, (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)),
        #     (3, (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5)),
        #     ((0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5)),
        #     (6, (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)),
        #     (6, 3, (0.5, -0.5, -0.5), (0.5, -0.5, 0.5)),
        #     ((-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5))])*.99 + np.array([x, y, z])


        normals = [(-1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0)]

        if len(color) ==3:
            glColor3fv(color)
        else:
            glColor4fv(color)
        glBegin(GL_QUADS)
        for i in xrange(6):
            glNormal3f(normals[i][0], normals[i][1], normals[i][2])
            for j in xrange(4):
                glVertex3f(vertices[i][j][0], vertices[i][j][1], vertices[i][j][2])
        glEnd()

    def draw_sphere(self, position, color, r=.25):
        glPushMatrix()
        glTranslatef(*position)
        glColor3fv(color)
        glutSolidSphere(r, 250, 250)
        glPopMatrix()

    def clear(self):
        self.gl_lists = []

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

                elif e.type == KEYDOWN and e.key == K_g:
                    self.draw_grid = not self.draw_grid

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # RENDER OBJECT
            glTranslate(self.tx/20., self.ty/20., - self.zpos)
            glRotate(self.ry, 1, 0, 0)
            glRotate(self.rx, 0, 1, 0)

            for gl_list in self.gl_lists:
                glCallList(gl_list)

            glLineWidth(1)
            if self.draw_grid:
                glCallList(G_OBJ_PLANE)
            # self.drawText((0,0), 'hello world')
            pygame.display.flip()
