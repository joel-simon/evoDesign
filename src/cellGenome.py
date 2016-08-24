from neat.genome import Genome
from .neat_custom.genes import AttributeGene, MorphogenGene

from copy import copy
from random import random, choice, gauss

class CellGenome(Genome):
    """Extend the default genome with more behavior."""
    def __init__(self, ID, config, parent1_id, parent2_id):
        super(CellGenome, self).__init__(ID, config, parent1_id, parent2_id)
        self.attribute_genes = {}
        self.genome_config = config.genome_config
        self.modules = [ M(**mc) for M, mc in self.genome_config['modules'] ]
        self.node_names = {}
        self.non_module_inputs  = len(config.genome_config['inputs'])
        self.non_module_outputs = len(config.genome_config['outputs'])

        self.update_inout()

    def update_inout(self):
        """
        Calculate the number of input and output nodes so the rest of
        NEAT can work properly.
        """
        # Lists of node names.
        self.inputs = copy(self.config.genome_config['inputs'])
        self.outputs = copy(self.config.genome_config['outputs'])

        for module in self.modules:
            self.inputs.extend(module.inputs)
            self.outputs.extend(module.outputs)

        self.num_inputs  = len(self.inputs)
        self.num_outputs = len(self.outputs)

    def create_module_gene(self, module, innovation_indexer):
        # print 'create_module_gene'
        assert(module in self.modules)
        module_gene = module.create_gene()
        in_genes = []
        out_genes = []

        # Each module recieves a 1000 block,
        # each gene recieves a 50 block (20 genes per module max).
        ID = 1000 * (self.modules.index(module)) + len(module.genes)*50

        for i, name in enumerate(module_gene.inputs):
            assert ID not in self.node_genes
            ng = self.config.node_gene_type(ID, 'INPUT')
            self.node_genes[ng.ID] = ng
            self.node_names[ng.ID] = name
            module_gene.node_genes.append(ng.ID)
            in_genes.append(ng)
            ID += 1

        for i, (name, act_func) in enumerate(module_gene.outputs):
            assert ID not in self.node_genes
            ng = self.config.node_gene_type(ID, 'OUTPUT', activation_type=act_func)
            self.node_genes[ng.ID] = ng
            self.node_names[ng.ID] = name
            module_gene.node_genes.append(ng.ID)
            out_genes.append(ng)
            ID += 1

        # TODO use config here
        if False: #  use fs_neat
            # Randomly connect one input to all hidden and output nodes (FS-NEAT).
            ig = choice(in_genes)
            # out_genes = [g for g in self.node_genes.values() if g.type == 'OUTPUT']
            for og in out_genes:
                weight = gauss(0, self.config.weight_stdev)
                innovation_id = innovation_indexer.get_innovation_id(ig.ID, og.ID)
                cg = self.config.conn_gene_type(innovation_id, ig.ID, og.ID, weight, True)
                self.conn_genes[cg.key] = cg


        self.update_inout()
        return module_gene

    def remove_module_gene(self, module, gene):
        nodes_to_delete = set()
        keys_to_delete = set()

        for n_id, node in gene.node_genes:
            nodes_to_delete.add(n_id)

        for key, value in self.conn_genes.items():
            if value.in_node_id in nodes_to_delete or value.out_node_id in nodes_to_delete:
                keys_to_delete.add(key)

        for key in keys_to_delete:
            del self.conn_genes[key]

        for n_id in nodes_to_delete:
            del self.node_genes[n_id]

        module.genes.remove(gene)

        assert len(self.conn_genes) > 0
        assert len(self.node_genes) >= self.num_inputs + self.num_outputs

        # return node_id

    def inherit_genes(self, parent1, parent2):
        """ Applies the crossover operator to modules. """
        super(CellGenome, self).inherit_genes(parent1, parent2)
        assert(len(parent1.modules) == len(parent2.modules))
        for mg, mg1, mg2 in zip(self.modules, parent1.modules, parent2.modules):
            for g_id, g1 in mg1.genes.items():
                mg.genes[g_id] = g1.copy()
                mg.inputs.extend(g1.inputs)
                mg.outputs.extend(g1.outputs)

        self.node_names = copy(parent1.node_names)
        self.valid()
        self.update_inout()

    def mutate(self, innovation_indexer):
        for ag in self.attribute_genes.values():
            ag.mutate(self.config)

        for module in self.modules:
            self.mutate_module(module, innovation_indexer)

        self.update_inout()

        super(CellGenome, self).mutate(innovation_indexer)

        return self

    def valid(self):
        for module in self.modules:
            # assert(len(module.inputs) = len(module.genes))
            for gene in module.genes.values():
                assert(len(gene.node_genes) == len(gene.inputs) + len(gene.outputs))
                for n_id in gene.node_genes:
                    assert(n_id in self.node_genes)

    def mutate_module(self, module, innovation_indexer):
        assert(module in self.modules)
        for gene in module.genes.values():
            gene.mutate()

        # Add gene
        if module.gene and len(module.genes) < module.max_genes and random() < module.prob_add:
            self.create_module_gene(module, innovation_indexer)

        # TODO Remove gene
        # if random() < module.prob_remove:
        #     self.genes.remove(choice(self.genes))

        self.valid()

    # Override create_unconnected function. to take custom activation_types.
    @classmethod
    def create_unconnected(cls, ID, config):
        '''Create a genome for a network with no hidden nodes and no connections.'''
        c = cls(ID, config, None, None)
        node_id = 0

        for name in c.inputs:
            assert node_id not in c.node_genes
            c.node_genes[node_id] = config.node_gene_type(node_id, 'INPUT')
            c.node_names[node_id] = name
            node_id += 1

        for name, act_type in c.outputs:
            assert node_id not in c.node_genes
            node_gene = config.node_gene_type(node_id,
                                              node_type='OUTPUT',
                                              activation_type=act_type)
            c.node_names[node_id] = name
            c.node_genes[node_gene.ID] = node_gene
            node_id += 1

        # print('have create_unconnected',node_id, len(c.node_genes), c.num_inputs)
        # assert node_id == len(c.node_genes)
        for module in c.modules:
            for i in range(module.min_genes):
                c.create_module_gene(module, None)
        return c

    def __str__(self):
        s = '#'*80 + '\n'
        s += 'Inputs:' + str(self.inputs)
        s += '\nOutputs:' + str(self.outputs) + '\n'
        s += super(CellGenome, self).__str__()
        s += '\nModules:\n'
        for module in self.modules:
            s += '\t'+str(module)
        s += '\n' + '#'*80
        return s
