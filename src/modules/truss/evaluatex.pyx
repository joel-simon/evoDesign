import numpy as np
cimport numpy as np

import cython
cimport cython

from libc.math cimport sqrt

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

ITYPE = np.int64
ctypedef np.int64_t ITYPE_t

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False) # turn off negative index wrapping for entire function
@cython.cdivision(True)
@cython.nonecheck(False)
cpdef the_forces(np.ndarray[DTYPE_t, ndim=1] elastic_modulus, \
                 np.ndarray[DTYPE_t, ndim=2] coordinates, \
                 np.ndarray[ITYPE_t, ndim=2] connections, \
                 np.ndarray[DTYPE_t, ndim=2] reactions, \
                 np.ndarray[DTYPE_t, ndim=2] loads, \
                 np.ndarray[DTYPE_t, ndim=1] area):

    cdef ITYPE_t jj, ii, k, i, u, j
    cdef DTYPE_t length, ea_over_l

    cdef np.ndarray[ITYPE_t, ndim=1] w
    cdef np.ndarray[DTYPE_t, ndim=1] flat_deflections, flat_loads, forces
    cdef np.ndarray[DTYPE_t, ndim=2] SSff

    cdef int n_cons = connections.shape[0]
    cdef np.ndarray[DTYPE_t, ndim=2] tj = np.zeros([n_cons, 3], dtype=DTYPE)

    w = np.array([np.size(reactions, axis=0), np.size(reactions, axis=1)], dtype=ITYPE)
    cdef np.ndarray[DTYPE_t, ndim=2] dof = np.zeros([3*w[1], 3*w[1]], dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=2] deflections = np.ones(w, dtype=DTYPE)
    deflections -= reactions

    # This identifies joints that can be loaded
    cdef np.ndarray[ITYPE_t, ndim=1] ff = np.where(deflections.T.flat == 1)[0]
    cdef np.ndarray[ITYPE_t, ndim=1] e = np.zeros((6), dtype=ITYPE)
    cdef np.ndarray[ITYPE_t, ndim=1] ends = np.zeros((3), dtype=ITYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] lv = np.zeros((3), dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] direction = np.zeros((3), dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=2] s = np.zeros((3, 3), dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=2] ss = np.zeros((6, 6), dtype=DTYPE)

    cdef ITYPE_t len_ff = len(ff)

    # Build the global stiffness matrix
    for i in xrange(n_cons):
        ends[0] = connections[i, 0]
        ends[1] = connections[i, 1]
        ends[2] = connections[i, 2]

        lv[0] = coordinates[ends[1],0] - coordinates[ends[0],0]
        lv[1] = coordinates[ends[1],1] - coordinates[ends[0],1]
        lv[2] = coordinates[ends[1],2] - coordinates[ends[0],2]

        length = sqrt(lv[0]*lv[0] + lv[1]*lv[1] + lv[2]*lv[2])

        direction[0] = lv[0]/length
        direction[1] = lv[1]/length
        direction[2] = lv[2]/length

        ea_over_l = elastic_modulus[i]*area[i] / length

        # Compute "s = np.outer(direction, direction)"
        for ii in xrange(3):
            for jj in xrange(3):
                s[ii, jj] = ea_over_l * direction[ii] * direction[jj]

        for u in xrange(3):
            for j in xrange(3):
                ss[u, j] = s[u, j]
                ss[u, j+3] = -1 * s[u, j]
                ss[u+3, j] = -1 * s[u, j]
                ss[u+3, j+3] = s[u, j]

        tj[i][0] = ea_over_l*direction[0]
        tj[i][1] = ea_over_l*direction[1]
        tj[i][2] = ea_over_l*direction[2]

        for k in xrange(6):
            e[k] = 3*ends[k/3] + k%3

        for ii in xrange(6):
            for jj in xrange(6):
                dof[e[ii], e[jj]] += ss[ii, jj]

    SSff = np.zeros([len_ff, len_ff])
    for i in xrange(len_ff):
        for j in xrange(len_ff):
            SSff[i, j] = dof[ff[i], ff[j]]

    flat_loads = loads.T.flat[ff]
    flat_deflections = np.linalg.solve(SSff, flat_loads)
    ff2 = np.where(deflections.T == 1)

    for i in xrange(len(ff2[0])):
        deflections[ff2[1][i], ff2[0][i]] = flat_deflections[i]

    forces = np.sum(np.multiply(
        tj.T, deflections[:, connections[:, 1]]
        - deflections[:, connections[:, 0]]), axis=0)

    # Check the condition number, and warn the user if it is out of range
    # cond = np.linalg.cond(SSff)

    # Compute the reactions
    # reactions = np.sum(dof*deflections.T.flat[:], axis=1).reshape([w[1], w[0]]).T

    return forces, deflections, reactions#, cond
