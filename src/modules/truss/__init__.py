import pyximport
import numpy
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)
import time
import math
from src.modules import Module, BaseModuleSimulation
from cellBody import CellBody
from src.modules.truss.truss import Truss
from src.modules.truss.draw import draw_truss

from numpy.linalg import LinAlgError
from src.map_utils import empty, shape
from os import path


SQRT3 = math.sqrt(3)

class TrussSimulation(BaseModuleSimulation):
    """docstring for TrussSimulation"""
    def __init__(self, simulation, module, is_static, get_load, cell_width):
        super(TrussSimulation, self).__init__(simulation, module)
        self.is_static = is_static
        self.get_load = get_load
        self.cell_width = cell_width

        self.truss = Truss()
        X, Y, Z = simulation.bounds
        self.joint_map = empty((X+1, Y+1, Z+1))
        self.joint_positions = empty((X+1, Y+1, Z+1))

    def cell_init(self, cell):
        w = self.cell_width
        # p = (cell.position[0]/w,cell.position[0]/w,cell.position[0]/w)
        cell.userData['stress'] = 0.0
        cell.userData['body'] = CellBody(
            ID=cell.id,
            truss=self.truss,
            position=cell.position,
            cell_width=self.cell_width,
            joint_map=self.joint_map,
            is_static=self.is_static,
            get_load=self.get_load,
        )

    def cell_destroy(self, cell):
        if 'body' in cell.userData:
            body = cell.userData['body']
            body.destroy()

    def update_truss(self):
        X, Y, Z = self.simulation.bounds
        joint_positions = numpy.zeros((X+1, Y+1, Z+1, 3),dtype='float64')
        counts = numpy.zeros((X+1, Y+1, Z+1),dtype='float64')

        for cell in self.simulation.cells:
            body = cell.userData['body']
            x, y, z = cell.position
            foo = [(0,0,0), (1,0,0), (1, 0, 1), (0, 0, 1), (0,1,0), (1, 1,0), (1, 1, 1), (0, 1, 1)]
            for i, (dx, dy, dz) in enumerate(foo):
                joint_positions[x+dx,y+dy,z+dz] += body.joint_positions[i]
                counts[x+dx,y+dy,z+dz] += 1

        for x in range(X+1):
            for y in range(Y+1):
                for z in range(Z+1):
                    if self.joint_map[x][y][z]:
                        joint_positions[x,y,z] /= counts[x,y,z]
                        self.joint_map[x][y][z].coordinates = joint_positions[x,y,z]

        for member in self.truss.members:
            parents = set(member.joint_a.userData['parents'])
            parents.update(member.joint_b.userData['parents'])
            r = sum(p.thickness for p in parents) / float(len(parents))
            member.r = r

    def calculate(self):
        if len(self.simulation.cells) == 0:
            return

        self.update_truss()

        try:
            self.truss.calc_fos()
        except LinAlgError as e:
            self.truss.fos_total = 0
            return

        for cell in self.simulation.cells:
            if 'body' in cell.userData:
                body = cell.userData['body']
                cell.userData['fos'] = min(m.fos for m in body.members)

    def handle_output(self, cell, outputs):
        # """ The phsyics module has no outputs.
        # """
        body = cell.userData['body']
        # Scales are in range (0, 1)

        scale = []
        scale.append(max(min(1.8, outputs[0]*2), .2))
        scale.append(max(min(1.8, outputs[1]*2), .2))
        scale.append(max(min(1.8, outputs[2]*2), .2))

        body.set_thickness(max(.02, outputs[3]*.2))
        body.set_scale(scale)

    def create_input(self, cell):
        """
        """
        if 'fos' in cell.userData:
            return [cell.userData['fos']-1]
        else:
            return [0]

    def save(self, directory):
        file = path.join(directory, 'truss.trs')
        self.truss.save(file)

    def render(self, viewer):
        draw_truss(viewer, self.truss, scale=1.0/self.cell_width)

class TrussModule(Module):
    """docstring for PhysicsModule"""
    name = 'truss'
    def __init__(self, is_static, get_load, cell_width):
        super(TrussModule, self).__init__(gene=None,
                                          simulation=TrussSimulation)

        self.simulation_config = {'is_static': is_static, 'get_load': get_load, 'cell_width': cell_width}

        self.inputs = ['fos']
        self.outputs = [('scale_x', 'sigmoid'), ('scale_y', 'sigmoid'),
                        ('scale_z', 'sigmoid'), ('thickness', 'sigmoid')]

