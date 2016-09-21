import unittest
import doctest

import os
from src.cellGenome import CellGenome
from neat import genome
from neat.config import Config
from neat.indexer import InnovationIndexer

from src.modules import Module, BaseModuleGene, BaseModuleSimulation
from src.modules.signals.signal_0 import Signal0Module, Signal0Gene

# from neat import visualize

def valid_genome(genome):

    in_genes = [g for g in genome.node_genes.values() if g.type == 'INPUT']
    hid_genes = [g for g in genome.node_genes.values() if g.type == 'HIDDEN']
    out_genes = [g for g in genome.node_genes.values() if g.type == 'OUTPUT']

    assert(len(genome.inputs) == genome.num_inputs)
    assert(len(in_genes) == genome.num_inputs)
    assert(len(genome.outputs) == genome.num_outputs)
    assert(len(out_genes) == genome.num_outputs)
    assert(len(set(genome.inputs)) == len(genome.inputs))

    for module in genome.modules:
        assert(len(module.genes) >= module.min_genes)
        if module.max_genes != None:
            assert(len(module.genes) <= module.max_genes)

        assert(set(module.total_inputs()) <= set(genome.inputs))
        assert(set(module.total_outputs()) <= set(genome.outputs))

        for gene in module.genes.values():
            assert(set(gene.node_gene_ids) <= set(genome.node_genes.keys()))
            assert(set(gene.inputs) <= set(genome.inputs))
            assert(set(gene.outputs) <= set(genome.outputs))
            assert(len(gene.node_gene_ids) == len(gene.inputs)+len(gene.outputs))


class Test_CellGenome(unittest.TestCase):
    """Unit tests for ."""
    def setUp(self):
        local_dir = os.path.dirname(__file__)
        self.indexer = InnovationIndexer(0)
        self.config = Config(os.path.join(local_dir, 'config.txt'))

        self.prob_add = 0
        self.prob_remove = 0
        self.min_genes = 2
        self.max_genes = 3

        self.genome_config = {
            'inputs': ['in0', 'in1'],
            'outputs': [('out0', 'sigmoid')],
            'modules': [
                (Signal0Module, {'prob_add':self.prob_add,
                                 'prob_remove':self.prob_remove,
                                 'min_genes':self.min_genes,
                                 'max_genes':self.max_genes})
            ]
        }

        self.config.genome_config = self.genome_config
        self.genome = CellGenome.create_unconnected(1, self.config)
        self.genome.connect_full(self.indexer)

    def test_init(self):
        valid_genome(self.genome)

    def test_init_module(self):
        """ Confirm signalModule was created correctly.
        """
        genome = self.genome
        module = genome.modules[0]

        # Confirm module is in genome.
        self.assertEqual(len(genome.modules), len(self.genome_config['modules']))

        # Cofirm settings are correct
        self.assertEqual(module.prob_add, self.prob_add)
        self.assertEqual(module.min_genes, self.min_genes)
        self.assertEqual(module.max_genes, self.max_genes)

    def test_init_genes(self):
        """ The cell_gene should have one signal0 gene and its inputs/outputs
        """
        genome = self.genome
        module = genome.modules[0]

        self.assertEqual(len(module.genes), self.min_genes)

        self.assertEqual(len(module.total_inputs()), 1 * self.min_genes)
        self.assertEqual(len(module.total_outputs()), 1 * self.min_genes)

    def test_init_genome(self):
        """ The cell genome must be updated with inputs and outputs
            Variables to sync: inputs, outputs, num_inputs, num_outputs
        """
        genome = self.genome
        module = genome.modules[0]

        true_inputs = self.genome_config['inputs'] + module.total_inputs()
        true_outputs = self.genome_config['outputs'] + module.total_outputs()

        self.assertEqual(set(genome.inputs), set(true_inputs))
        self.assertEqual(set(genome.outputs), set(true_outputs))

        self.assertEqual(genome.num_inputs, len(true_inputs))
        self.assertEqual(genome.num_outputs, len(true_outputs))

        self.assertTrue(all(isinstance(i, str) for i in genome.inputs))
        self.assertTrue(all(isinstance(o, tuple) for o in genome.outputs))
        self.assertTrue(all(len(o) == 2 for o in genome.outputs))

        self.assertEqual(genome.non_module_inputs, len(self.genome_config['inputs']))
        self.assertEqual(genome.non_module_outputs, len(self.genome_config['outputs']))

    def test_add_gene(self):
        genome = self.genome
        module = genome.modules[0]

        module.prob_add = 1
        genome.mutate_module(module, self.indexer)

        self.assertEqual(len(module.genes), self.min_genes + 1)
        # visualize.draw_net(self.genome,
        #                    view=True,
        #                    node_names=self.genome.node_names,
        #                    filename="add_gene.gv"
        #                    )
        valid_genome(self.genome)

    def test_remove_gene(self):
        genome = self.genome
        module = genome.modules[0]
        module.min_genes -= 1

        genome.remove_module_gene(module)
        self.assertEqual(len(module.genes), module.min_genes)
        # visualize.draw_net(self.genome,
        #                    view=True,
        #                    node_names=self.genome.node_names,
        #                    filename="remove_gene.gv"
        #                    )
        # print module.genes
        # print genome.node_genes.keys()

        # module.prob_add = 1
        # genome.mutate_module(module, self.indexer)
        # print module.genes
        # print genome.node_genes.keys()

        valid_genome(self.genome)


    def test_crossover(self):
        """ Crossover module with same number of genes
        """
        genome2 = CellGenome.create_unconnected(1, self.config)
        genome2.connect_full(self.indexer)

        self.genome.fitness = 1
        genome2.fitness = 0

        child = self.genome.crossover(genome2, child_id=3)
        self.assertEqual(len(child.modules[0].genes), len(genome2.modules[0].genes))
        valid_genome(child)

    def test_crossover2(self):
        """ Crossover module with parent 1 having more genes
            Child should get additional genes.
        """
        genome2 = CellGenome.create_unconnected(1, self.config)
        genome2.connect_full(self.indexer)

        # Give parent1 with higher score new gene.
        self.genome.create_unconnected_mgene(self.genome.modules[0])

        self.genome.fitness = 1
        genome2.fitness = 0

        child = self.genome.crossover(genome2, child_id=3)
        self.assertEqual(len(child.modules[0].genes), len(self.genome.modules[0].genes))
        valid_genome(child)

    def test_crossover3(self):
        """ Crossover module with parent 2 having more genes
            Child should NOT get additional genes.
        """
        genome2 = CellGenome.create_unconnected(1, self.config)
        genome2.connect_full(self.indexer)

        # Give parent1 with higher score new gene.
        genome2.create_unconnected_mgene(genome2.modules[0])

        self.genome.fitness = 1
        genome2.fitness = 0

        child = self.genome.crossover(genome2, child_id=3)
        self.assertEqual(len(child.modules[0].genes), len(self.genome.modules[0].genes))

        valid_genome(child)
        valid_genome(self.genome)
        valid_genome(genome2)


    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()
