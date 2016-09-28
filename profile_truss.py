import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

import pickle
import time
# from src.modules.truss.truss import handle_results
from src.modules.truss.handle_results import handle_results
truss, results = pickle.load(open('test_truss.p', 'r'))
start = time.time()
n = 10

for i in range(n):
    handle_results(truss, *results)

print 'done', (time.time()-start)/n
