"""
A program to simulate basic pattern formation based on
short range enhancement and long range repression.
From Gierer and Meinhardt, 1972,
A theory of biological pattern formation

author: tinri aegerter / prasenjit saha
"""

from scipy import randn
from numpy import array, zeros_like, arange, random, ones
import pylab
import matplotlib
from matplotlib.pyplot import figure, show, plot
from matplotlib.animation import FuncAnimation

steps = 2000 #number of iteration steps
n = 40       #number of regions on the x-axis
deltat=1     #duration of time steps used
Da = 0.01    #diffusion of the activator (unit: , if regions on x-axis have a width of 1 mu)
Ra = 0.005    #removal rate of the activator
Pa = 0.02   #activator-independent activator production rate

Db = 0.4     #Diffusion of the inhibitor
Rb = 0.03    #Removal rate of the inhibitor

S=(random.rand(n)*.1+1)*Ra
a=ones([n]) #concentration of activator
b=ones([n]) #concentration of inhibitor

def init():
    pass
    # for i in range(0,n):
    #     S[i]=Ra*(1+0.01*randn(1))
    #     a[i]=1
    #     b[i]=1

fig = figure()
p = fig.add_subplot(111)
p.set_ylim(0,5)
a_for_plot = p.plot(range(0,n),a)[0]
b_for_plot = p.plot(range(0,n),b)[0]


def clocktick():
    global a,b
    a_new = zeros_like(a)
    b_new = zeros_like(b)
    for i in range(0, n):

        #activator
        Prod_a=(S[i]*(a[i]**2)/b[i])+Pa   # production
        Rem_a=(Ra*a[i])                   # removal
        if i==0: #boundary condition left
            Dif_a=Da*(a[1]-a[0])
        elif i==n-1: #boundary condition left
            Dif_a=Da*(a[n-2]-a[n-1])
        else: #general
            Dif_a=Da*(a[i-1]+a[i+1]-2*a[i])

        a_new[i]=a[i]+Prod_a-Rem_a+Dif_a

        #inhibitor
        Prod_b=(S[i]*a[i]**2)             # production
        Rem_b=(Rb*b[i])                   # removal
        if i==0: #boundary condition left
            Dif_b=Db*(b[1]-b[0])
        elif i==n-1: #boundary condition left
            Dif_b=Db*(b[n-2]-b[n-1])
        else: #general
            Dif_b=Db*((b[i-1]-b[i])+(b[i+1]-b[i]))
        b_new[i]=b[i]+Prod_b-Rem_b+Dif_b

    a=a_new
    b=b_new
    print b.max()



def animate(t):
    print "t= ",t
    if t==0:
            init()
    else:
            clocktick()
    a_for_plot.set_ydata(a)
    b_for_plot.set_ydata(a)
    # if t%200 == 0:
    #         fig.savefig('frame%02d.png'%(t/200))

ani = FuncAnimation(fig, animate, range(steps+1), interval=25)

show()
pylab.show()
