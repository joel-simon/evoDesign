
# coding: utf-8

# In[12]:

from array import array
import time
import numpy as np


# In[19]:

n = 1000000


# In[21]:

print 'numpy'
a = np.zeros([0])
start = time.time()
for _ in range(n):
    np.append(a, 1.0)
print time.time() - start
print

# In[30]:

print 'python array'
a = array('d', [])
start = time.time()
for _ in range(n):
    a.append(1.0)
print time.time() - start

start = time.time()
for _ in range(1000):
    del a[0]
print time.time() - start

start = time.time()
np.array(a)
print time.time() - start
print

# In[29]:
print 'python list'
a = []
start = time.time()
for _ in range(n):
    a.append(1.0)
print time.time() - start


start = time.time()
for _ in range(1000):
    del a[0]
print time.time() - start


start = time.time()
np.array(a)
print time.time() - start
print

# In[ ]:



