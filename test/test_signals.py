import unittest
import doctest

import os
from src.cellGenome import CellGenome
from neat import genome
from neat.config import Config
from neat.indexer import InnovationIndexer

from src.modules import Module, BaseModuleGene, BaseModuleSimulation
from src.modules.signals import Signal0Gene, Signal0Simulation

class Test_CellGenome(unittest.TestCase):
    """Unit tests for ."""
    def setUp(self):
        local_dir = os.path.dirname(__file__)
        indexer = InnovationIndexer(0)
        config = Config(os.path.join(local_dir, 'test_config.txt'))

        self.genome_config = {
            'inputs':['in0', 'in1'],
            'outputs':[('out0', 'sigmoid')],
            'modules' : [
                (Module, {'gene':Signal0Gene,
                          'simulation':Signal0Simulation,
                          'prob_add':0, 'min_genes':1, 'max_genes':1 })
            ]
        }

        config.genome_config = self.genome_config
        self.genome = CellGenome.create_unconnected(1, config)
    
    def test_inouts(self):
        g = self.genome
        n_in = len(self.genome_config['inputs']) + 1
        n_out = len(self.genome_config['outputs']) + 1
        assert(len(g.inputs) == n_in)
        assert(len(g.outputs) == n_out)
        assert(g.num_inputs == n_in)
        assert(g.num_outputs == n_out)
        assert(all(isinstance(i, str) for i in g.inputs))
        assert(all(isinstance(o, tuple) for o in g.outputs))
        assert(all(len(o) == 2 for o in g.outputs))
        assert(g.non_module_inputs == len(self.genome_config['inputs']))
        assert(g.non_module_outputs == len(self.genome_config['outputs']))

    def test_genes(self):
        g = self.genome
        ins = self.genome_config['inputs']
        outs = self.genome_config['outputs']
        
        for gene in g.modules[0].genes.values():
            ins.extend(gene.inputs)
            outs.extend(gene.outputs)

        out_names = [o[0] for o in outs]
        print g.node_names.values()
        assert(len(g.modules[0].genes) == 1)
        assert(len(g.node_names) == len(ins)+len(outs))
        assert(len(g.node_genes) == len(ins)+len(outs))
        assert(set(g.node_names.values()) == set(ins+out_names))

    # def test_simulation(self):
    #     sim = self.genome.modules[0].create_simulation()
    #     sim

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
