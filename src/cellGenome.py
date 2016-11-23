from __future__ import print_function
from neat.genome import Genome
from .neat_custom.genes import AttributeGene, MorphogenGene

from copy import copy
from random import random, choice, gauss, shuffle

def valid_genome(genome):
    # return
    """ Only for testing. Do not use in production.
    """
    in_genes = [g for g in genome.node_genes.values() if g.type == 'INPUT']
    hid_genes = [g for g in genome.node_genes.values() if g.type == 'HIDDEN']
    out_genes = [g for g in genome.node_genes.values() if g.type == 'OUTPUT']

    assert(len(genome.inputs) == genome.num_inputs)
    assert(len(in_genes) == genome.num_inputs)
    assert(len(genome.inputs) == len(set(genome.inputs))) # No repeats

    assert(len(genome.outputs) == genome.num_outputs)
    assert(len(out_genes) == genome.num_outputs)
    assert(len(genome.outputs) == len(set(genome.outputs))) # No repeats

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


class CellGenome(Genome):
    """Extend the default genome with more behavior."""
    def __init__(self, ID, config, parent1_id, parent2_id):
        super(CellGenome, self).__init__(ID, config, parent1_id, parent2_id)
        self.attribute_genes = {}
        self.genome_config = config.genome_config

        module_configs = self.genome_config['modules']#.items()
        self.modules = [M(**mconf) for (M, mconf) in module_configs]

        self.node_names = {}
        self.non_module_inputs  = len(config.genome_config['inputs'])
        self.non_module_outputs = len(config.genome_config['outputs'])

        self.inputs = copy(self.config.genome_config['inputs'])
        self.outputs = copy(self.config.genome_config['outputs'])

        for module in self.modules:
            self.inputs.extend(module.inputs)
            self.outputs.extend(module.outputs)

        self.num_inputs = len(self.inputs)
        self.num_outputs = len(self.outputs)

    def inherit_genes(self, parent1, parent2):
        """ Applies the crossover operator to modules.
            The mgene nodes are autoamtically inherited but without the mgene object.
        """
        super(CellGenome, self).inherit_genes(parent1, parent2)
        assert(len(self.modules) == len(parent1.modules))
        assert(len(self.modules) == len(parent2.modules))

        for i, module in enumerate(self.modules):
            p1_module = parent1.modules[i]
            p2_module = parent2.modules[i]

            # For every module_gene in the module
            for mg_id, mg1 in p1_module.genes.items():
                if mg_id in p2_module.genes:
                    mg2 = p2_module.genes[mg_id]
                    module.genes[mg_id] = mg1.get_child(mg2)
                else:
                    module.genes[mg_id] = mg1.copy()

                self.inputs.extend(module.genes[mg_id].inputs)
                self.outputs.extend(module.genes[mg_id].outputs)
                self.num_inputs += len(module.genes[mg_id].inputs)
                self.num_outputs += len(module.genes[mg_id].outputs)

        self.node_names = copy(parent1.node_names)

    def mutate(self, innovation_indexer):
        for ag in self.attribute_genes.values():
            ag.mutate(self.config)

        # All modules
        for module in self.modules:
            self.mutate_module(module, innovation_indexer)

        super(CellGenome, self).mutate(innovation_indexer)

        return self

    def remove_module_gene(self, module):
        # valid_genome(self)
        gene_id, mgene = choice(module.genes.items())
        nodes_to_delete = set(mgene.node_gene_ids)
        conns_to_delete = []

        # print(self)

        for key, value in self.conn_genes.items():
            if value.in_node_id in nodes_to_delete or value.out_node_id in nodes_to_delete:
                conns_to_delete.append(key)

        for conn_id in conns_to_delete:
            del self.conn_genes[conn_id]

        for node_id in nodes_to_delete:
            del self.node_genes[node_id]

        del module.genes[gene_id]

        self.num_inputs -= len(mgene.inputs)
        self.num_outputs -= len(mgene.outputs)

        for input in mgene.inputs:
            self.inputs.remove(input)
        for output in mgene.outputs:
            self.outputs.remove(output)

        # print(self)
        # valid_genome(self)

    def mutate_module(self, module, innovation_indexer):
        """ Called by self.mutate
        """
        if module.gene is None:
            return

        for gene in module.genes.values():
            gene.mutate()

        # Add mgene
        if random() < module.prob_add and len(module.genes) < module.max_genes:
            mgene = self.create_unconnected_mgene(module)

            if self.config.initial_connection == 'fully_connected':
                self.connect_mgene_full(mgene, innovation_indexer)

            elif self.config.initial_connection == 'partial':
                self.connect_mgene_partial(mgene, innovation_indexer, self.config.connection_fraction)

            elif self.config.initial_connection == 'fs_neat':
                raise NotImplementedError

        # Remove mgene
        if random() < module.prob_remove and len(module.genes) > module.min_genes:
            self.remove_module_gene(module)
        # valid_genome(self)

    def add_connection(self, g1, g2, innovation_indexer):
        weight = gauss(0, self.config.weight_stdev)
        innovation_id = innovation_indexer.get_innovation_id(g1.ID, g2.ID)
        cg = self.config.conn_gene_type(innovation_id, g1.ID, g2.ID, weight, True)
        self.conn_genes[cg.key] = cg

    def mutate_add_connection(self, innovation_indexer):
        '''
        Overrride this function to prevent connections between outputs. 
        '''
        in_node = choice(list(self.node_genes.values()))
        
        if in_node.type == 'OUTPUT':
            return

        possible_outputs = [n for n in self.node_genes.values() if n.type != 'INPUT']
        out_node = choice(possible_outputs)

        # Only create the connection if it doesn't already exist.
        key = (in_node.ID, out_node.ID)
        if key not in self.conn_genes:
            self.add_connection(in_node, out_node, innovation_indexer)

    def compute_full_mgene_connections(self, mgene):
        in_genes = [g for g in self.node_genes.values() if g.type == 'INPUT']
        hid_genes = [g for g in self.node_genes.values() if g.type == 'HIDDEN']
        out_genes = [g for g in self.node_genes.values() if g.type == 'OUTPUT']

        mgene_nodes = [self.node_genes[ID] for ID in mgene.node_gene_ids]
        new_in = [g for g in mgene_nodes if g.type == 'INPUT']
        new_out = [g for g in mgene_nodes if g.type == 'OUTPUT']

        connections = []

        for ng in new_in:
            for og in hid_genes + out_genes:
                connections.append((ng, og))

        for og in new_out:
            for ig in hid_genes + [g for g in in_genes if g not in new_in]:
                connections.append((ig, og))

        return connections

    def connect_mgene_full(self, mgene, innovation_indexer):
        for g1, g2 in self.compute_full_mgene_connections(mgene):
            self.add_connection(g1, g2, innovation_indexer)

    def connect_mgene_partial(self, mgene, innovation_indexer, fraction):
        assert 0 <= fraction <= 1
        all_connections = self.compute_full_connections()
        shuffle(all_connections)
        num_to_add = int(round(len(all_connections) * fraction))
        for g1, g2 in all_connections[:num_to_add]:
            self.add_connection(g1, g2, innovation_indexer)

    def create_unconnected_mgene(self, module):
        mgene = module.create_gene()

        self.inputs.extend(mgene.inputs)
        self.outputs.extend(mgene.outputs)
        self.num_inputs += len(mgene.inputs)
        self.num_outputs += len(mgene.outputs)

        # Each module recieves a 1000 block
        # Each gene recieves a 50 block (20 genes per module max).
        ID = 1000*(self.modules.index(module)+1) + mgene.ID*50

        for name in mgene.inputs:
            if ID in self.node_genes:
                print(ID)
                print(name)
                print(self)

            assert ID not in self.node_genes
            ng = self.config.node_gene_type(ID, 'INPUT')
            self.node_genes[ng.ID] = ng
            self.node_names[ng.ID] = name
            mgene.node_gene_ids.append(ng.ID)
            ID += 1

        for (name, act_func) in mgene.outputs:
            assert ID not in self.node_genes
            ng = self.config.node_gene_type(ID, 'OUTPUT', activation_type=act_func)
            self.node_genes[ng.ID] = ng
            self.node_names[ng.ID] = name
            mgene.node_gene_ids.append(ng.ID)
            ID += 1

        # valid_genome(self)
        return mgene

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

        for module in c.modules:
            for i in range(module.start_genes):
                c.create_unconnected_mgene(module)
            # print(module, len(module.genes))
        # assert(False)
        # valid_genome(c)
        return c

    def __str__(self):
        s = '#'*80 + '\n'
        s += 'Inputs:\n\t' + ', '.join(self.inputs)
        s += '\nOutputs:\n\t' + '; '.join(n+':'+t for n, t in self.outputs)
        s += '\nModules:\n'
        for module in self.modules:
            s += '\t'+str(module)+'\n'
            for gene in module.genes.values():
                s+= '\t\t' + str(gene) + '\n'
        # s += '\n'
        s += super(CellGenome, self).__str__()
        s += '\n' + '#'*80
        return s
