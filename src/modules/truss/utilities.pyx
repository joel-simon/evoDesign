import numpy as np
cimport numpy as np

import cython
cimport cython

from libc.math cimport sqrt, M_PI, pow, abs

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

ITYPE = np.int64
ctypedef np.int64_t ITYPE_t

cpdef prepare(truss):
    cdef ITYPE_t num_members = len(truss.members)
    cdef ITYPE_t num_joints = len(truss.joints)

    cdef np.ndarray[DTYPE_t, ndim=1] area = np.zeros((num_members,))
    # cdef np.ndarray[DTYPE_t, ndim=1] lengths = np.zeros((num_members,))

    cdef np.ndarray[ITYPE_t, ndim=2] connections = \
                                        np.zeros((num_members,2), dtype='int64')

    cdef double r
    cdef int i
    jti = truss.joint_to_idx
    for i in range(num_members):
        m = truss.members[i]
        r = m.r
        connections[i][0] = jti[m.joint_a]
        connections[i][1] = jti[m.joint_b]

        area[i] = M_PI * r * r

    return area, connections