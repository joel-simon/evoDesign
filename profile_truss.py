import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

import pickle
import time
# from src.modules.truss.truss import handle_results
from src.modules.truss.handle_results import handle_results
truss, results = pickle.load(open('test_truss.p', 'r'))

n = 1
start = time.time()
for i in range(n):
	truss.calc_fos()
print 'done', (time.time()-start)/n



# for i in range(n):
#     handle_results(truss, *results)

