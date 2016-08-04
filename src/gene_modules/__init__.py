from random import random, choice
from copy import copy

class GeneModuleGene(object):
    def __init__(self, ID):
        self.ID = ID
        # self.num_inputs = len(self.inputs)
        # self.num_outputs = len(self.outputs)

        self.node_genes = []

    def handle_output(self, cell, outputs):
        raise NotImplemented

    def mutate(self):
        pass

    def create_input(self, cell, sim):
        raise NotImplemented

    def step(self):
        raise NotImplemented

    def copy(self):
        raise NotImplemented

    def create_child(self):
        raise NotImplemented

class GeneModule(object):
    def __init__(self, gene, gene_config={}, prob_add=.1, prob_remove=.02,
                                                min_genes=0, max_genes=None):
        self.min_genes = min_genes
        self.max_genes = max_genes
        self.prob_add = prob_add
        self.prob_remove = prob_remove
        self.gene = gene
        self.gene_config = gene_config
        # self.signals = [ Signal(**signal_config) for _ in range(min) ]

        self.genes = {}

    def next_id(self):
        return len(self.genes)

    # def __str__(self):
    #     return 'GeneModule'# % (self.num_inputs, self.num_outputs)

    def create_gene(self):
        ID = self.next_id()
        gene = self.gene(ID, **self.gene_config)
        self.genes[ID] = gene
        return gene

    def destroy_gene(self, gene):
        pass

    def handle_output(self, cell, outputs):
        for i in range(len(self.genes)):
            k = len(self.genes[i].outputs)
            self.genes[i].handle_output(cell, outputs[(i*k) : (i*k+k)])

    def create_input(self, cell, sim):
        inputs = sum([s.create_input(cell, sim) for s in self.genes.values()], [])
        # assert(len(inputs) == self.num_inputs)
        return inputs
