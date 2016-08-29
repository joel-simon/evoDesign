import numpy as np
import time

def evaluate(reactions, coords, loads, connections, E, A):
    num_joints = reactions.shape[1]
    num_members = connections.shape[1]

    assert(reactions.dtype) == 'bool'
    assert(coords.dtype) == 'float32'
    assert(loads.dtype) == 'float32'
    assert(connections.dtype == 'int32')

    assert(reactions.shape == (3, num_joints))
    assert(coords.shape[0] == num_joints)
    assert(coords.shape[1] == 3)
    assert(loads.shape == (num_joints, 3))
    assert(connections.shape[0] == 2)
    assert(len(E) == num_members)
    assert(len(A) == num_members)

    start = time.time()

    tj = np.zeros([3, np.size(connections, axis=1)])
    w = np.array([np.size(reactions, axis=0), np.size(reactions, axis=1)])
    dof = np.zeros([3*w[1], 3*w[1]])

    deflections = np.ones(w) - reactions

    # This identifies joints that can be loaded
    ff = np.where(deflections.T.flat == 1)[0]
    # ff2 = np.where(deflections.flat == 1)

    # print('point a: %f' % (time.time() - start))

    # Build the global stiffness matrix
    for i in range(np.size(connections, axis=1)):
        ends = connections[:, i]
        length_vector = coords[ends[1]] - coords[ends[0]]

        length = np.linalg.norm(length_vector)
        direction = length_vector/length
        d2 = np.outer(direction, direction)
        ea_over_l = E[i]*A[i] / length
        ss = ea_over_l*np.concatenate((np.concatenate((d2, -d2), axis=1),
                                          np.concatenate((-d2, d2), axis=1)), axis=0)
        tj[:, i] = ea_over_l*direction
        e = list(range((3*ends[0]), (3*ends[0] + 3))) \
            + list(range((3*ends[1]), (3*ends[1] + 3)))
        for ii in range(6):
            for j in range(6):
                dof[e[ii], e[j]] += ss[ii, j]

    # print('point b: %f' %(time.time() - start))
    # print len(ff)

    SSff = np.zeros([len(ff), len(ff)])
    for i in range(len(ff)):
        for j in range(len(ff)):
            SSff[i, j] = dof[ff[i], ff[j]]

    flat_loads = loads.flat[ff]

    # print('point c: %f' %(time.time() - start))

    flat_deflections = np.linalg.solve(SSff, flat_loads)

    # print('point d: %f' %(time.time() - start))

    ff = np.where(deflections.T == 1)
    for i in range(len(ff[0])):
        deflections[ff[1][i], ff[0][i]] = flat_deflections[i]
    forces = np.sum(np.multiply(
        tj, deflections[:, connections[1]]
        - deflections[:, connections[0]]), axis=0)

    # Check the condition number, and warn the user if it is out of range
    # cond = np.linalg.cond(SSff)

    # Compute the reactions
    # reactions = np.sum(dof*deflections.T.flat[:], axis=1)\
    #     .reshape([w[1], w[0]]).T
    # print('evaluate_forces ran in: %f' %(time.time() - start))
    return forces, deflections#, reactions#, cond
