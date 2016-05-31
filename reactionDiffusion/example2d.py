def fix_boundaries(systems, boundaries):
    for i in xrange(len(systems)):
        systems[i][0, :] = boundaries[i]
        systems[i][-1, :] = boundaries[i]
        systems[i][:, 0] = boundaries[i]
        systems[i][:, -1] = boundaries[i]

    return systems

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal as sig
import cPickle as pickle


# Approach
# begin in steady state homogenous (X = A, Y = B/A).  at t = 50, add 0.1 to the centre pixel.
# for A = 1, D1 = 0.2, D2 =0.02, and 0.1 < B < 1.75 , the system reaches a steady state with chaotic spatial patterns
# for B = 1.8, we get fractured boundary and random chaotic oscillations

# 0.7 2.7 0.1 0.2 - life like

# 0.2 1.4 0.1 0.08 - creepy crawly

A, B = 1, 2.21
D1, D2 = 0.2,  0.02

LENGTH = 30
WIDTH = 30

SHOW = 10
dt = 0.1

RUN = 1000
PERTURB = 20
PERTURB_STRENGTH = 0.1
MODE = 1 # 0 for single perturb, 1 for many

B_A = B if A == 0 else B/A

class System():
    def __init__(self, params, init_cond, dt, show, L, W, run_time, perturb_time, perturb_strength, perturb_mode):

        # Fixed concentrations
        self.A = params[0]
        self.B = params[1]

        # Diffusion coefficients
        self.D1 = params[2]
        self.D2 = params[3]

        # Initial conditions
        self.chem1 = init_cond[0]
        self.chem2 = init_cond[1]

        # system definitions
        self.dt = dt
        self.L = L
        self.W = W
        self.run_time = run_time
        self.show = show
        self.time = 0
        self.perturb_time = perturb_time
        self.perturb_mode = perturb_mode
        self.perturb_strength = perturb_strength

        # Laplace operator
        self.L2 = 0.25*np.asarray([[0, 1, 0], [1, -4, 1], [0, 1, 0]])

    def step(self):
        update_chem1 = np.zeros((self.L, self.W))
        update_chem2 = np.zeros((self.L, self.W))

        # compute second derrivatives for diffusion
        L2_chem1 = sig.convolve2d(self.chem1, self.L2, mode = 'same')
        L2_chem2 = sig.convolve2d(self.chem2, self.L2, mode = 'same')

        # system of equations
        dChem1 = self.D1*L2_chem1 + self.A + (self.chem1**2)*self.chem2 - (self.B + 1)*self.chem1
        dChem2 = self.D2*L2_chem2 + self.B*self.chem1 - (self.chem1**2)*self.chem2

        update_chem1 += dChem1*self.dt
        update_chem2 += dChem2*self.dt

        self.chem1 += update_chem1
        self.chem2 += update_chem2

        # for physicality and stability
        self.chem1[self.chem1 < 0] = 0
        self.chem2[self.chem2 < 0] = 0
        self.chem1[self.chem1 > 10] = 10
        self.chem2[self.chem2 > 10] = 10

        # perturb system
        # if self.perturb_mode == 0:
        #     if self.time == self.perturb_time:
        #         self.chem2[self.L/2, self.W/2] += self.perturb_strength
        # elif self.perturb_mode == 1:
        #     if self.time % self.perturb_time == 0:
        #         self.chem2[np.random.randint(0, self.L-1), np.random.randint(0, self.W-1)] += self.perturb_strength
        # elif self.perturb_mode == 2:
        #     if self.time % self.perturb_time == 0:
        #         self.chem1 += np.random.normal(0, self.perturb_strength, self.chem1.shape)
        #         self.chem2 += np.random.normal(0, self.perturb_strength, self.chem2.shape)


        self.chem1, self.chem2 = fix_boundaries([self.chem1, self.chem2], [A, B_A])


    def run(self):
        plt.ion()

        #chem1Display = plt.subplot(211)
        chem2Display = plt.subplot(111)

        #chem1 = chem1Display.imshow(self.chem1, cmap = 'cool', interpolation = 'nearest')
        chem2 = chem2Display.imshow(self.chem2, cmap = 'cool')#, interpolation = 'nearest')

        while self.time < self.run_time:
            self.step()
            #chem1.set_data(self.chem1)
            chem2.set_data(self.chem2)

            if self.time % self.show == 0:
                #chem1.autoscale()
                chem2.autoscale()
                plt.draw()
                #plt.pause(0.05)

            self.time += 1

# initialize
chem1_init = (np.random.randn(LENGTH, WIDTH)*.01 + 1)*A
chem2_init =  (np.random.randn(LENGTH, WIDTH)*.01 + 1)*B_A
react_diff = System([A, B, D1, D2], [chem1_init, chem2_init], dt, SHOW, LENGTH, WIDTH, RUN, PERTURB, PERTURB_STRENGTH, MODE)
react_diff.run()

plt.ioff()
plt.show()
