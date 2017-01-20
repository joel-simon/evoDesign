from random import random, choice
from copy import copy

class BaseModuleSimulation(object):
    """ A module may have its own simulation where it handles its logic. """

    def __init__(self, simulation, module, num_inputs=0, num_outputs=0,
                                                             has_render=False):
        self.simulation = simulation
        self.module = module
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.has_render = has_render

    def cell_init(self, x, y, z):
        pass

    def cell_destroy(self, x, y, z):
        pass

    def handle_output(self, x, y, z, outputs, current, next):
        pass

    def create_input(self, x, y, z, input, current):
        pass

    def step(self):
        pass

    def save(self, directory):
        pass

    # def render(self, surface):
    #     pass

class BaseModuleGene(object):
    """
        A module may have a gene. This gene is contians multiple inputs
        and outputs.
    """
    def __init__(self, ID, inputs, outputs):
        self.ID = ID
        self.node_gene_ids = []
        self.inputs = inputs
        self.outputs = outputs

    def mutate(self):
        raise NotImplementedError()

    def copy(self):
        S = self.__class__(self.ID)
        S.inputs = copy(self.inputs)
        S.outputs = copy(self.outputs)
        S.node_gene_ids = copy(self.node_gene_ids)
        return S

    def get_child(self, other):
        """ Default has no crossover operation.
        """
        return self.copy()

    def __str__(self):
        ids_str = ', '.join(map(str, self.node_gene_ids))
        return "ModuleGene(ID=%i, node_gene_ids=[%s])" % (self.ID, ids_str)

class Module(object):
    """ A module is a discrete group of logic that connects cells, their state
        and their inputs and outputs.
    """
    def __init__(self, gene, simulation,
                 gene_config={}, prob_add=.2, prob_remove=.1,
                 min_genes=0, start_genes=None,  max_genes=99):
        self.gene = gene
        self.gene_config = gene_config

        self.simulation = simulation
        self.simulation_config = dict()

        # Gene config data
        assert(min_genes <= max_genes)
        self.min_genes = min_genes
        self.max_genes = max_genes

        if start_genes is None:
            self.start_genes = min_genes
        else:
            assert(start_genes <= max_genes and start_genes >= min_genes)
            self.start_genes = start_genes

        self.prob_add = prob_add
        self.prob_remove = prob_remove

        # TODO: maybe genes have different connection configs
        # self.initial_connection = initial_connection

        # These are not part of module genes.
        self.inputs = []
        self.outputs = []

        # id => instance of gene
        self.genes = {}
        self.next_gene_id = 0

    def __str__(self):
        mod = self.__class__.__name__
        gene = self.gene.__name__ if self.gene else 'None'
        sim = self.simulation.__name__ if self.simulation else 'None'
        return "%s(gene:%s, simulation:%s, num_genes=%i)" % (mod, gene, sim, len(self.genes))

    def total_inputs(self):
        return sum((g.inputs for g in self.genes.values()), self.inputs)

    def total_outputs(self):
        return sum((g.outputs for g in self.genes.values()), self.outputs)

    def next_id(self):
        # gid = self.next_gene_id
        # self.next_gene_id += 1
        gid = 0#len(self.genes)
        while gid in self.genes:
            gid += 1
        return gid

    def create_gene(self):
        ID = self.next_id()
        gene = self.gene(ID, **self.gene_config)
        assert ID not in self.genes
        self.genes[ID] = gene
        return gene

    # def destroy_gene(self, gene):
    #     raise NotImplementedError

    def create_simulation(self):
        """ An instance of a modules simulation class is owned by parent simulation """
        return self.simulation(**self.simulation_config)
