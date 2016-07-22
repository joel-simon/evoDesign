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

dots = {'Da':.005,'Di':.18,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':False}
salt_pepper = {'Da':.0,'Di':.2,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':True}
thin_strips = {'Da':.0,'Di':.01,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':True}

gradient = {'Da':.005,'Di':.18,'Ra':.01,'Ri':.01,'Pa':.001,'Pi':.001, 'saturate':False}

spread_morphogen(
    A = A,
    I = make_array(size, 1),
    step=draw_hex_map,
    steps=5000,
    **gradient
)
print('function took %0.3f ms' % ((time.time()-time1)*1000.0))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()



