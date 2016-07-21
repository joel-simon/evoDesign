import sys
import pyximport; pyximport.install()
import time
from morphx import spread_morphogen, make_array
import random

import pygame
from hexRenderer import draw_hex_map


time1 = time.time()

A = make_array(40, 1)
for row in range(len(A)):
    for col in range(len(A[0])):
        A[row][col] += random.random() *2

dots = {'Da':.005,'Di':.18,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001}
a = {'Da':.005,'Di':.18,'Ra':.02,'Ri':1,'Pa':.001,'Pi':0}

spread_morphogen(
    A = A,
    H = make_array(40, 0),
    saturate=False,
    step=draw_hex_map,
    steps=3000,
    **dots
)
print('function took %0.3f ms' % ((time.time()-time1)*1000.0))
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()



