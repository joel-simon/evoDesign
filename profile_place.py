import numpy
import pyximport
pyximport.install(setup_args={"include_dirs":numpy.get_include()},
                  reload_support=True)

import pickle
import time
from examples.bookcase import place, placex

data = pickle.load(open('place_data.p', 'r'))

n = 10000
start = time.time()
for i in range(n):
	place.place_items(*data)
print 'done', (time.time()-start)/n

start = time.time()
for i in range(n):
	placex.place_items(*data)
print 'done', (time.time()-start)/n


# for i in range(n):
#     handle_results(truss, *results)

