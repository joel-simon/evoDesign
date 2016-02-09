import numpy

def numpy_where(array):
    if len(array.shape) == 1:
        foo = []
        for i in range(array.shape[0]):
            if array[i]:
                foo.append(i)
        # return (np.array([i for i, v in enumerate(),)
        return (numpy.array(foo), )

    assert(len(array.shape) == 2)
    out = ([], [])

    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            if array[i,j]:
                out[0].append(i)
                out[1].append(j)

    # out[0] = numpy.array(out[0])
    # out[1] = numpy.array(out[1])
    return (numpy.array(out[0]), numpy.array(out[1]))

if __name__ == '__main__':
    # print(numpy_where(numpy.array([[0, 1], [1, 0]])))
    # np.where(
    # (array([0, 1]), array([1, 0]))
    a = numpy.array([0,1,0,1])
    print(numpy_where(a == 1))

def the_forces(truss_info):
    tj = numpy.zeros([3, numpy.size(truss_info["connections"], axis=1)])
    w = numpy.array([numpy.size(truss_info["reactions"], axis=0),
                     numpy.size(truss_info["reactions"], axis=1)])
    dof = numpy.zeros([3*w[1], 3*w[1]])
    deflections = numpy.ones(w)
    deflections -= truss_info["reactions"]

    # This identifies joints that can be loaded
    ff = numpy_where(deflections.T.flat == 1)[0]

    # Build the global stiffness matrix
    for i in range(numpy.size(truss_info["connections"], axis=1)):
        ends = truss_info["connections"][:, i]
        length_vector = truss_info["coordinates"][:, ends[1]] \
            - truss_info["coordinates"][:, ends[0]]
        length = numpy.linalg.norm(length_vector)
        direction = length_vector/length
        d2 = numpy.outer(direction, direction)
        ea_over_l = truss_info["elastic_modulus"][i]*truss_info["area"][i]\
            / length
        ss = ea_over_l*numpy.concatenate((numpy.concatenate((d2, -d2), axis=1),
                                          numpy.concatenate((-d2, d2), axis=1)),
                                         axis=0)
        tj[:, i] = ea_over_l*direction
        e = list(range((3*ends[0]), (3*ends[0] + 3))) \
            + list(range((3*ends[1]), (3*ends[1] + 3)))
        for ii in range(6):
            for j in range(6):
                dof[e[ii], e[j]] += ss[ii, j]

    SSff = numpy.zeros([len(ff), len(ff)])
    for i in range(len(ff)):
        for j in range(len(ff)):
            SSff[i, j] = dof[ff[i], ff[j]]

    flat_loads = truss_info["loads"].T.flat[ff]
    flat_deflections = numpy.linalg.solve(SSff, flat_loads)

    ff = numpy_where(deflections.T == 1)
    for i in range(len(ff[0])):
        deflections[ff[1][i], ff[0][i]] = flat_deflections[i]
    forces = numpy.sum(numpy.multiply(
        tj, deflections[:, truss_info["connections"][1, :]]
        - deflections[:, truss_info["connections"][0, :]]), axis=0)

    # Check the condition number, and warn the user if it is out of range
    cond = numpy.linalg.cond(SSff)

    # Compute the reactions
    reactions = numpy.sum(dof*deflections.T.flat[:], axis=1)\
        .reshape([w[1], w[0]]).T

    return forces, deflections, reactions, cond
