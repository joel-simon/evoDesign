import random

class AttributeGene(object):
    def __init__(self, ID, value = random.random()):
        assert(value >= 0 and value <= 1)
        self.ID = ID
        self.value = value
        self.min = 0.0
        self.max = 1.0

    def __str__(self):
        return 'Attribute Gene:'+str(self.value)

    def mutate(self, config):
        return
        r = random.random
        if r() < config.prob_mutate_weight:
            if r() < config.prob_replace_attribute:
                # Replace value with a random value.
                self.value = r()
            else:
                # Perturb value.
                value = self.value + random.gauss(0, 1) * config.attribute_mutation_power
                self.value = max(0, min(1.0, value))

    def copy(self):
        return AttributeGene(self.value)

    def get_child(self, other):
        """ Creates a new Gene randomly inheriting attributes from its parents."""
        return AttributeGene((self.value+other.value)/2)

class MorphogenGene(object):
    """docstring for MorphogenGene"""
    def __init__(
            self, ID,
            activator_diffusion=0.01,
            activator_decay=0.02,
            activator_production=0.0,

            inhibitor_diffusion=0.20,
            inhibitor_decay=0.02,
            inhibitor_production=0.0
        ):

        self.ID = ID
        self.components = dict()
        self.components['activator_diffusion'] = AttributeGene(1, activator_diffusion)
        self.components['activator_decay'] = AttributeGene(1, activator_decay)
        self.components['activator_production'] = AttributeGene(1, activator_production)

        self.components['inhibitor_diffusion'] = AttributeGene(1, inhibitor_diffusion)
        self.components['inhibitor_decay'] = AttributeGene(1, inhibitor_decay)
        self.components['inhibitor_production'] = AttributeGene(1, inhibitor_production)


    def mutate(self, config):
        for gene in self.components.values():
            gene.mutate(config)

    def values(self):
        return { name: gene.value for name, gene in self.components.items() }

    # def copy(self):
    #     pg = PheromoneGene( self.ID,
    #                         self.strength_gene.copy(),
    #                         self.decay_gene.copy(),
    #                         self.distance_gene.copy())
    #     return pg

    # def get_child(self, other):
    #     # print(self.ID , other.ID)
    #     assert(self.ID == other.ID)

    #     """ Creates a new Gene randomly inheriting attributes from its parents."""
    #     strength_gene = random.choice([self.strength_gene, other.strength_gene])
    #     distance_gene = random.choice([self.distance_gene, other.distance_gene])
    #     decay_gene    = random.choice([self.decay_gene, other.decay_gene])
    #     child = PheromoneGene( self.ID, strength_gene, distance_gene, decay_gene )
    #     return child
