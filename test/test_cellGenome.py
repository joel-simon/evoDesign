import unittest
import doctest

import os
from src.cellGenome import CellGenome
from neat import genome
from neat.config import Config
from neat.indexer import InnovationIndexer

class Test_CellGenome(unittest.TestCase):
    """Unit tests for ."""
    def setUp(self):
        local_dir = os.path.dirname(__file__)
        indexer = InnovationIndexer(0)
        config = Config(os.path.join(local_dir, 'config.txt'))

        self.genome_config = {
            'inputs':['in0', 'in1'],
            'outputs':[('out0', 'sigmoid')],
            'modules' : [
            ]
        }
        config.genome_config = self.genome_config
        self.genome = CellGenome.create_unconnected(1, config)

    def test_inouts(self):
        g = self.genome
        n_in = len(self.genome_config['inputs'])
        n_out = len(self.genome_config['outputs'])
        self.assertEqual(len(g.inputs), n_in)
        self.assertEqual(len(g.outputs), n_out)
        self.assertEqual(g.num_inputs, n_in)
        self.assertEqual(g.num_outputs, n_out)
        self.assertTrue(all(isinstance(i, str) for i in g.inputs))
        self.assertTrue(all(isinstance(o, tuple) for o in g.outputs))
        self.assertTrue(all(len(o) == 2 for o in g.outputs))
        self.assertEqual(g.non_module_inputs, n_in)
        self.assertEqual(g.non_module_outputs, n_out)

    def test_genes(self):
        g = self.genome
        ins = self.genome_config['inputs']
        outs = self.genome_config['outputs']
        out_names = [o[0] for o in outs]
        self.assertEqual(len(g.node_names), len(ins)+len(outs))
        self.assertEqual(len(g.node_genes), len(ins)+len(outs))
        self.assertEqual(set(g.node_names.values()), set(ins+out_names))

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
