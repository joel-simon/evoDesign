# Reaction-Diffusion Simulation Using Gray-Scott Model
# https://en.wikipedia.org/wiki/Reaction-diffusion_system
# http://www.labri.fr/perso/nrougier/teaching/numpy/numpy.html#
# FB - 20160130
import random
import numpy as np
from PIL import Image, ImageDraw
n = 16
imgx = n; imgy = n # image size
image = Image.new("RGB", (imgx, imgy))
draw = ImageDraw.Draw(image)
pixels = image.load()
steps = 10000

params = []
params.append((0.16, 0.08, 0.035, 0.065)) # Bacteria 1
params.append((0.14, 0.06, 0.035, 0.065)) # Bacteria 2
params.append((0.16, 0.08, 0.060, 0.062)) # Coral
params.append((0.19, 0.05, 0.060, 0.062)) # Fingerprint
params.append((0.10, 0.10, 0.018, 0.050)) # Spirals
params.append((0.12, 0.08, 0.020, 0.050)) # Spirals Dense
params.append((0.10, 0.16, 0.020, 0.050)) # Spirals Fast
params.append((0.16, 0.08, 0.020, 0.055)) # Unstable
params.append((0.16, 0.08, 0.050, 0.065)) # Worms 1
params.append((0.16, 0.08, 0.054, 0.063)) # Worms 2
params.append((0.16, 0.08, 0.035, 0.060)) # Zebrafish
(Du, Dv, F, k) = (.005, .18, )#random.choice(params)

# dots = {'Da':.005,'Di':.18,'Ra':.02,'Ri':.02,'Pa':.001,'Pi':.001, 'saturate':False}

Z = np.zeros((n+2,n+2), [('U', np.double), ('V', np.double)])
U,V = Z['U'], Z['V']
u,v = U[1:-1,1:-1], V[1:-1,1:-1]

r = 20
u[...] = 1.0
U[n/2-r:n/2+r,n/2-r:n/2+r] = 0.50
V[n/2-r:n/2+r,n/2-r:n/2+r] = 0.25
u += 0.05*np.random.random((n,n))
v += 0.05*np.random.random((n,n))

p = 0
for i in xrange(steps):
    Lu = (                 U[0:-2,1:-1] +
          U[1:-1,0:-2] - 4*U[1:-1,1:-1] + U[1:-1,2:] +
                           U[2:  ,1:-1] )
    Lv = (                 V[0:-2,1:-1] +
          V[1:-1,0:-2] - 4*V[1:-1,1:-1] + V[1:-1,2:] +
                           V[2:  ,1:-1] )
    # uvv = u*v*v
    # u += (Du*Lu - uvv +  F   *(1-u))
    # v += (Dv*Lv + uvv - (F+k)*v    )
    # uvv = u*v*v
    # u += (Du*Lu - uvv +  F   *(1-u))
    # v += (Dv*Lv + uvv - (F+k)*v    )

    pn = 100 * (i + 1) / steps # percent completed
    if pn != p:
        p = pn
        print "%" + str(p).zfill(2)

# paint the final state
vMin=V.min(); vMax=V.max()
for iy in range(imgy):
    for ix in range(imgx):
        w = V[iy, ix]
        c = int(255 * (w - vMin) / (vMax - vMin))
        pixels[ix, iy] = (c, c, c)
label = "Du=" + str(Du) + " Dv=" + str(Dv) + " F=" + str(F) + " k=" + str(k)
draw.text((0, 0), label, (0, 255, 0))
image.save("ReactionDiffusionSim.png", "PNG")
