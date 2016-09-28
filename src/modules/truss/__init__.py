import pyximport
import numpy
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)
import time
import math
from src.modules import Module, BaseModuleSimulation
from cellBody import CellBody
from src.modules.truss.truss import Truss
from numpy.linalg import LinAlgError
from src.map_utils import empty
SQRT3 = math.sqrt(3)

class TrussSimulation(BaseModuleSimulation):
    """docstring for TrussSimulation"""
    def __init__(self, simulation, module, static_map):
        super(TrussSimulation, self).__init__(simulation, module)
        self.static_map = static_map
        self.radius = 1
        self.truss = Truss()
        X, Y, Z = simulation.bounds
        self.joint_map = empty((X+1, Y+1, Z+1))

    def cell_init(self, cell):
        cell.userData['stress'] = 0.0
        cell.userData['body'] = CellBody(
            ID=cell.id,
            truss=self.truss,
            position=cell.position,
            joint_map=self.joint_map,
        )

    def cell_destroy(self, cell):
        if 'body' in cell.userData:
            body = cell.userData['body']
            body.destroy()

    def calculate(self):
        if len(self.simulation.cells) == 0:
            return
        try:
            self.truss.calc_fos()
        except LinAlgError as e:
            print('LinAlgError!')
            self.truss.fos_total = 0
            for member in self.truss.members:
                member.fos = 0

        for cell in self.simulation.cells:
            if 'body' in cell.userData:
                body = cell.userData['body']
                cell.userData['fos'] = min(m.fos for m in body.members)

    def handle_output(self, cell, outputs):
        """ The phsyics module has no outputs.
        """
        pass

    def create_input(self, cell):
        """
        """
        if 'fos' in cell.userData:
            return [cell.userData['fos']-1]
        else:
            return [0]

    def render(self, view):
        nodes = [j.coordinates+j.deflections.T for j in self.truss.joints]
        edges = [(self.truss.joint_index(m.joint_a), self.truss.joint_index(m.joint_b)) \
                                                    for m in self.truss.members]

        colors = [(1-min(1, m.fos), 0, 0) for m in self.truss.members]
        if self.simulation.verbose:
            print('Rendering truss. %i nodes,  %i edges.'%(len(nodes), len(edges)))
        view.add_mesh(nodes, edges, colors)

class TrussModule(Module):
    """docstring for PhysicsModule"""
    def __init__(self, static_map):
        super(TrussModule, self).__init__(gene=None,
                                            simulation=TrussSimulation)

        self.simulation_config = {'static_map': static_map}

        self.inputs = ['fos']
        self.outputs = []

