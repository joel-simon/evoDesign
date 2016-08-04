import os
from src.cellGenome import CellGenome
from neat import genome
from neat.config import Config
from neat.indexer import InnovationIndexer

from src.gene_modules import signals

local_dir = os.path.dirname(__file__)
indexer = InnovationIndexer(0)
config = Config(os.path.join(local_dir, 'config.txt'))

config.genome_config = {
    'inputs':['in0','in1'],
    'outputs':[('out0', 'sigmoid')],
    'gene_modules':[{ 'gene': signals.Signal0 }]
}


def inherit4():
    """ B
    """
    genome1 = CellGenome.create_unconnected(1, config)
    genome2 = CellGenome.create_unconnected(2, config)
    genome1.fitness = 1.0
    genome2.fitness = 0.0

    genome1.create_module_gene(genome1.gene_modules[0],indexer)
    genome1.create_module_gene(genome1.gene_modules[0],indexer)

    genome2.create_module_gene(genome2.gene_modules[0],indexer)
    genome2.create_module_gene(genome2.gene_modules[0],indexer)

    child = genome1.crossover(genome2, 3)
    assert(len(child.gene_modules[0].genes) == 2)
    # print child
    child.create_module_gene(child.gene_modules[0],indexer)
    print child
    # print child.num_inputs
    child.valid()
    assert(len(child.gene_modules[0].genes) == 3)

inherit4()
#
