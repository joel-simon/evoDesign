import time
import random

plot = True

if plot:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    from matplotlib.ticker import LinearLocator, FormatStrFormatter

def make_array(n, v=0):
    if type(v) == type(lambda n:n):
        return [[v() for x in range(n)] for y in range(n)]
    else:
        return [[v for x in range(n)] for y in range(n)]

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap

@timing
def run(steps, w, Da, Ra, Pa, Db, Rb, Pb, S, saturate=False):
    a = make_array(w, 1) #concentration of activator
    b = make_array(w, 1) #concentration of inhibitor

    a_new = make_array(w, 0)
    b_new = make_array(w, 0)

    if plot:
        plt.ion()
        chem_a = plt.imshow(a, interpolation='none', cmap = 'cool')
        plt.title('activator')
        plt.colorbar(chem_a)

    for s in xrange(steps):
        for i in xrange(w):
            for j in xrange(w):
                av = a[i][j]
                bv = b[i][j]
                Sv = S[i][j]

                #activator
                a_2 = (av**2)

                if saturate: 
                    a_2 /= (1+.2*a_2)

                if bv != 0:
                    Prod_a=(Sv*a_2/(bv))+Pa[i][j]   # production
                else:
                    Prod_a=(Sv*a_2)+Pa[i][j]

                Rem_a=(Ra*av)                   # removal

                Dif_a = 0.
                if i>0: Dif_a += a[i-1][j] - av #boundary condition top
                if i<w-1: Dif_a += a[i+1][j] - av #boundary condition bottom
                if j>0: Dif_a += a[i][j-1] - av #boundary condition left
                if j<w-1: Dif_a += a[i][j+1] - av #boundary condition right

                a_new[i][j]=av+Prod_a-Rem_a+(Da*Dif_a)

                #inhibitor
                Dif_b = 0.0
                Prod_b=(Sv*(av**2))+Pb           # production
                Rem_b=(Rb*bv)                   # removal

                if i>0: Dif_b += b[i-1][j] - bv #boundary condition top
                if i<w-1: Dif_b += b[i+1][j] - bv #boundary condition bottom
                if j>0: Dif_b += b[i][j-1] - bv #boundary condition left
                if j<w-1: Dif_b += b[i][j+1] - bv #boundary condition right

                b_new[i][j]=bv+Prod_b-Rem_b+(Db*Dif_b)

        # energy[s] = (a-a_new).sum()\
        a, a_new, = a_new, a
        b, b_new, = b_new, b
        if s%100==0:
            print s
        if plot and s%5 == 0:
            chem_a.set_data(a_new)
            chem_a.autoscale()
            plt.draw()
            # chem_b.set_data(b)

dots = {
    'Da': 0.01,
    'Ra': 0.02,
    # 'Pa': make_array(w, .001),
    'Db': 0.20,
    'Rb': 0.02,
    'Pb': 0.001
}

def main():
    steps = 2000 #number of iteration steps
    w = 40       #number of regions on the x-axis

    Da = 0.01    #diffusion of the activator (unit: , if regions on x-axis have a width of 1 mu)
    Ra = 0.02    #removal rate of the activator
    Pa = make_array(w, .001) #activator-independent activator production rate
    # Pa = make_array(w, lambda: (random.random()*.1))
    # Pa[0][19] = .1
    Pa[0][20] = .1
    # Pa[0][21] = .1

    Pa[20][20] = .1
    Pa[30][20] = .1

    Db = 0.20    #Diffusion of the inhibitor
    Rb = 0.02     #Removal rate of the inhibitor
    Pb = 0.001   #activator-independent inhibitor production rate

    # 'Source density' = Production of the activator, proportional to the decay rate +/- 1 % fluctiation
    S = make_array(w, 1)
    # S = make_array(w, lambda: (random.random()*.1 +1)*Ra)

    run(steps, w, Da, Ra, Pa, Db, Rb, Pb, S)
    print 'Done'
    if plot:
        plt.ioff()
        plt.show()

if __name__ == '__main__':
    main()
