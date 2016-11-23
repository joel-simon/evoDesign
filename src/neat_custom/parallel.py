from multiprocessing import Pool

class ParallelEvaluator(object):
    def __init__(self, num_workers, eval_function):
        '''
        eval_function should take one argument (a genome object) and return
        a single float (the genome's fitness).
        '''
        self.num_workers = num_workers
        self.eval_function = eval_function
        self.pool = Pool(num_workers)

    def evaluate(self, genomes):
        fitnesses = self.pool.map(self.eval_function, genomes)
        for fitness, genome in zip(fitnesses, genomes):
            genome.fitness = fitness
