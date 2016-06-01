from neat.genome import Genome
from neat_custom.genes import AttributeGene, MorphogenGene

# morphogen_thresholds = 4
# nodes_per_morphogen =

class CellGenome(Genome):
    """Extend the default genome with more behavior."""
    def __init__(self, *args, **kwargs):
        super(CellGenome, self).__init__(*args, **kwargs)

        self.cell_types = 1
        self.num_morphogens = 1
        self.morphogen_thresholds = 6

        self.morphogen_genes = dict()
        self.attribute_genes = dict()

        self.inputs = [
            'stress'
        ]

        self.outputs = [
            'apoptosis',
            'division'
        ]

        for i in range(self.num_morphogens):
            # Create the morphogen gene with ranodm values.
            self.morphogen_genes[i] = MorphogenGene(i)

            # Create the inputs and outputs for this morphogen.
            for t in range(self.morphogen_thresholds):
                self.inputs.append('a%it%i' % (i, t))

            self.outputs.extend(['a'+str(i), 'h'+str(i)])

        # print self.inputs
        self.num_inputs  = len(self.inputs)
        self.num_outputs = len(self.outputs)


    # def num_cell_inputs(self):
    #     num_inputs = 0
    #     # num_inputs = self.cell_types# One binary value for each cell type.
    #     num_inputs += self.num_morphogens*self.morphogen_thresholds
    #     return num_inputs

    # def num_cell_outputs(self):
    #     num_outputs = 1 # Apoptosis.
    #     num_outputs += 1 # Division.

    #     # num_outputs += self.cell_types - 1 # Cell division differentiation.
    #     # num_outputs += 4 # Cell division direction.
    #     num_outputs += self.num_morphogens*2 # 1 activation and 1 inhibition

    #     return num_outputs


    def mutate(self, innovation_indexer):
        super(CellGenome, self).mutate(innovation_indexer)

        # if conition:
        #   add or subtract morphogen

        for mg in self.morphogen_genes.values():
            mg.mutate(self.config)

        for ag in self.morphogen_genes.values():
            ag.mutate(self.config)

        return self

    def __str__(self):
        # s = 'Morphogens:'
        return super(CellGenome, self).__str__()

