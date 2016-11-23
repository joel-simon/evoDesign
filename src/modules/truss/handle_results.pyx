import numpy as np
cimport numpy as np

import cython
cimport cython

from libc.math cimport sqrt, M_PI, pow, abs

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

ITYPE = np.int64
ctypedef np.int64_t ITYPE_t

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False) # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.nonecheck(False)
cpdef handle_results(truss, np.ndarray[DTYPE_t, ndim=1] forces,
    np.ndarray[DTYPE_t, ndim=2] deflections, \
    np.ndarray[DTYPE_t, ndim=2] reactions):
    cdef DTYPE_t fos_total = 10000
    cdef DTYPE_t rho = 200
    cdef DTYPE_t elastic_modulus = 5e8
    cdef DTYPE_t Fy = 5e8

    cdef DTYPE_t force, length, moi, area, LW, mass, fos_buckling
    cdef DTYPE_t fos, fos_yielding, r, r2

    cdef np.ndarray[DTYPE_t, ndim=1] end_a, end_b

    cdef DTYPE_t PI2 = pow(M_PI, 2)

    cdef int i

    truss.mass = 0

    for i in range(len(truss.members)):
        m = truss.members[i]
        force = forces[i]

        end_a = m.joint_a.coordinates
        end_b = m.joint_b.coordinates

        x = pow(end_a[0]-end_b[0], 2)
        y = pow(end_a[1]-end_b[1], 2)
        z = pow(end_a[2]-end_b[2], 2)

        length = sqrt(x+y+z)
        r = m.r
        r2 = r*r

        moi = (M_PI/4)*r2*r2
        area = (M_PI*r2)
        LW = area * rho
        mass = length * LW

        if force != 0:
            fos_yielding = Fy * area / abs(force)
        else:
            fos_yielding = 10000

        if force != 0:
            fos_buckling = -((PI2)*elastic_modulus*moi/(length**2)) / force
            if fos_buckling <=0:
                fos_buckling = 10000
        else:
            fos_buckling = 10000

        if fos_yielding < fos_buckling:

            fos = fos_yielding
        else:
            fos = fos_buckling

        if fos < fos_total:
            fos_total = fos

        m.fos = fos
        truss.mass += mass

    for i in range(len(truss.joints)):
    #     if truss.translations[i]
    #     truss.joints[i].
        joint = truss.joints[i]
        for j in range(3):
            if joint.translation[j]:
                # truss.joints[i].reactions[j] = reactions[j, i]
                joint.deflections[j] = 0.0
            else:
                # truss.joints[i].reactions[j] = 0.0
                joint.deflections[j] = deflections[j, i]

    truss.fos_total = fos_total

    return

