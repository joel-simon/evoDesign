import random

class AttributeGene(object):
    def __init__(self, ID, value=random.random(), minv=0, maxv=1, mutate_power=None):
        assert(value >= 0 and value <= 1)
        self.ID = ID
        self.minv = minv
        self.maxv = maxv
        self.value = max(self.minv, min(self.maxv, value))
        if mutate_power == None:
            self.mutate_power = self.value/2

    def __str__(self):
        return 'Attribute Gene:'+str(self.value)

    def mutate(self, config):
        r = random.random
        if r() < .6:#config.prob_mutate_weight:
            if r() < .1:#config.prob_replace_attribute:
                # Replace value with a random value.
                self.value = random.uniform(self.minv, self.maxv)
            else:
                # Perturb value.
                self.value += random.gauss(0, 1) * self.mutate_power
            self.value = max(self.minv, min(self.maxv, self.value))

    def copy(self):
        return AttributeGene(self.value)

    def get_child(self, other):
        """ Creates a new Gene randomly inheriting attributes from its parents."""
        return AttributeGene((self.value+other.value)/2)

class MorphogenGene(object):
    """docstring for MorphogenGene"""
    def __init__(
            self, ID,
            activator_diffusion=0.02,
            activator_removal=0.02,
            # activator_production=0.001,

            inhibitor_diffusion=0.1,
            inhibitor_removal=0.02,
            # inhibitor_production=0.001
            saturate=False
        ):

        self.ID = ID
        self.saturate = saturate
        self.components = {
            'activator_diffusion' :  AttributeGene(1, activator_diffusion, maxv=.15),
            'activator_removal' :  AttributeGene(1, activator_removal, maxv=.5),
            # 'activator_production' :  AttributeGene(1, activator_production, maxv=.5),

            'inhibitor_diffusion' :  AttributeGene(1, inhibitor_diffusion, maxv=.15, minv=.001),
            'inhibitor_removal' :  AttributeGene(1, inhibitor_removal, maxv=.5),
            # 'inhibitor_production' :  AttributeGene(1, inhibitor_production, maxv=.5)
        }

    def mutate(self, config):
        # return
        if random.random() < .1:
            self.saturate = not self.saturate

        for gene in self.components.values():
            gene.mutate(config)

    def values(self):
        v = { name: gene.value for name, gene in self.components.items() }
        v['saturate'] = self.saturate
        return v

    # def copy(self):
    #     pg = PheromoneGene( self.ID,
    #                         self.strength_gene.copy(),
    #                         self.removal_gene.copy(),
    #                         self.distance_gene.copy())
    #     return pg

    # def get_child(self, other):
    #     # print(self.ID , other.ID)
    #     assert(self.ID == other.ID)

    #     """ Creates a new Gene randomly inheriting attributes from its parents."""
    #     strength_gene = random.choice([self.strength_gene, other.strength_gene])
    #     distance_gene = random.choice([self.distance_gene, other.distance_gene])
    #     removal_gene    = random.choice([self.removal_gene, other.removal_gene])
    #     child = PheromoneGene( self.ID, strength_gene, distance_gene, removal_gene )
    #     return child
