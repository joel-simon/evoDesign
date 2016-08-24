from random import random, choice
from copy import copy

class BaseModuleSimulation(object):
    """ A module may have its own simulation where it handles its logic. """
    
    def __init__(self, simulation, module, has_render=True):
        self.simulation = simulation
        self.module = module
        self.has_render = has_render

    def cell_init(self, cell):
        pass

    def cell_destroy(self, cell):
        pass

    def handle_output(self, cell, outputs):
        pass

    def create_input(self, cell):
        return []

    def step(self):
        pass

    def render(self, surface):
        raise NotImplementedError()

class BaseModuleGene(object):
    """
        A module may have a gene. This gene is contians multiple inputs
        and outputs.
    """
    def __init__(self, ID, inputs, outputs):
        self.ID = ID
        self.node_genes = []
        self.inputs = inputs
        self.outputs = outputs

    def mutate(self):
        raise NotImplementedError()

    def copy(self):
        raise NotImplementedError()

    def create_child(self):
        raise NotImplementedError()

class Module(object):
    """ A module is a discrete group of logic that connects cells, their state
        and their inputs and outputs.
    """
    def __init__(self, gene, simulation,
                 gene_config={}, prob_add=.1, prob_remove=.02,
                 min_genes=0, max_genes=None):

        self.gene = gene
        self.gene_config = gene_config

        self.simulation = simulation
        self.simulation_config = dict()

        self.min_genes = min_genes
        self.max_genes = max_genes
        self.prob_add = prob_add
        self.prob_remove = prob_remove

        self.inputs = []
        self.outputs = []
        self.genes = {}

    def __str__(self):
        mod = self.__class__.__name__
        gene = self.gene.__name__ if self.gene else 'None'
        sim = self.simulation.__name__ if self.simulation else 'None'
        return "%s(gene:%s, simulation:%s, num_genes=%i)" % (mod, gene, sim, len(self.genes))

    def next_id(self):
        return len(self.genes)

    def create_gene(self):
        ID = self.next_id()
        gene = self.gene(ID, **self.gene_config)
        self.genes[ID] = gene
        self.inputs.extend(gene.inputs)
        self.outputs.extend(gene.outputs)
        return gene

    def destroy_gene(self, gene):
        pass

    def create_simulation(self):
        """ An instance of a modules simulation class is owned by parent simulation """
        return self.simulation(**self.simulation_config)