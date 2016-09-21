import unittest
import doctest
import os
import numpy
from src.modules.truss.truss import Truss
# from src.modules.truss2.physical_properties import materials

class Test_CellGenome(unittest.TestCase):
    """Unit tests for ."""
    def setUp(self):
        truss = Truss()
        self.truss = truss
        j0 = truss.add_support([0.0, 0.0, 0.0])
        j1 = truss.add_joint([1.0, 0.0, 0.0])
        j2 = truss.add_joint([2.0, 0.0, 0.0])
        j3 = truss.add_joint([3.0, 0.0, 0.0])
        j4 = truss.add_joint([4.0, 0.0, 0.0])
        j5 = truss.add_support([5.0, 0.0, 0.0])

        j6 = truss.add_joint([0.5, 1.0, 0.0])
        j7 = truss.add_joint([1.5, 1.0, 0.0])
        j8 = truss.add_joint([2.5, 1.0, 0.0])
        j9 = truss.add_joint([3.5, 1.0, 0.0])
        j10 = truss.add_joint([4.5, 1.0, 0.0])

        j7.loads[1] = -20000
        j8.loads[1] = -20000
        j9.loads[1] = -20000

        truss.add_member(j0, j1)
        truss.add_member(j1, j2)
        truss.add_member(j2, j3)
        truss.add_member(j3, j4)
        truss.add_member(j4, j5)

        truss.add_member(j6, j7)
        truss.add_member(j7, j8)
        truss.add_member(j8, j9)
        truss.add_member(j9, j10)

        truss.add_member(j0, j6)
        truss.add_member(j6, j1)
        truss.add_member(j1, j7)
        truss.add_member(j7, j2)
        truss.add_member(j2, j8)
        truss.add_member(j8, j3)
        truss.add_member(j3, j9)
        truss.add_member(j9, j4)
        self.m1 = self.truss.add_member(j4, j10)
        self.m2 = self.truss.add_member(j10, j5)

        self.j4 = j4
        self.j5 = j5
        self.j10 = j10

        # for member in self.truss.members:
            # member.set_shape("pipe", update_props=True)
            # member.set_material("A36", update_props=True)
            # member.set_parameters(t=0.002, r=0.02, update_props=True)
            # member.set_shape("bar", update_props=True)
            # member.set_material("cell", update_props=True)
            # member.set_parameters(r=0.02, update_props=True)

    def test_truss(self):
        self.truss.calc_fos()
        self.truss.calc_mass()
        self.assertAlmostEqual(self.truss.fos_total, 7.75156917007)
        # self.assertAlmostEqual(self.truss.mass, 37.5825759882)
        return True

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
