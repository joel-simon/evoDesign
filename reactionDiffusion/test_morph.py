import sys
# import pyximport; pyximport.install()
import time
from morph import spread_morphogen, make_array
import random

import pygame
from hexRenderer import draw_hex_map
time1 = time.time()

size = 40

A = make_array(size, 1)
for row in range(len(A)):
    for col in range(len(A[0])):
        A[row][col] += random.random() *.1

I = make_array(size, 1)

dots = {'A':A,'I':I,'Da':.005,'Di':.18,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':False}
salt_pepper = {'A':A,'I':I,'Da':.0,'Di':.2,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':True}
thin_strips = {'A':A,'I':I,'Da':.0,'Di':.01,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':True}
gradient = {'A':A,'I':I,'Da':.005,'Di':.18,'Ra':.01,'Ri':.01,'Pa':.001,'Pi':.001, 'saturate':False}


center = {
    'A': make_array(size, 0),
    'I': make_array(size, 0),
    'Da':.005,
    'Di':.18,
    'Ra':.01,
    'Ri':.01,
    'Pa':make_array(size, 0),
    'Pi':make_array(size, 0),
     'saturate':False
}
center['Pa'][20][20] = .1
center['Pi'][20][20] = 0

spread_morphogen(
    step=draw_hex_map,
    steps=3000,
    **center
)
print('function took %0.3f ms' % ((time.time()-time1)*1000.0))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()



