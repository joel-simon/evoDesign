import numpy as np

square = np.array([[.5, -.5, -.5],[.5, .5, -.5],[-.5, .5, -.5],[-.5, -.5, -.5],
                   [.5, -.5, .5], [.5, .5, .5], [-.5, .5, .5], [-.5, -.5, .5]])

faces = np.array([[0, 1, 2, 3],[3, 2, 6, 7], [7, 6, 5, 4],
                  [0, 4, 5, 1], [1, 5, 6, 2], [0, 3, 7, 4]])

def to_obj(cmap, path=None, metadata=''):
    with open(path, 'w') as f:
        f.write('# Exported map mesh from BAUPLAN.\n')

        if metadata:
            f.write('#%s\n'%metadata)

        locations = list(zip(*np.where(cmap)))

        for (x, y, z) in locations:
            for vert in square + np.array([x, y, z]):
                vert += .5
                f.write('v %.3f %.3f %.3f\n'% tuple(vert))

        for i in range(len(locations)):
            for face in (faces + 8*i + 1):
                f.write('f %i %i %i %i\n' % tuple(reversed(face)))

# cmap = np.zeros([3,3,3])
# cmap[0,0,0] = 1
# cmap[0,1,0] = 1
# map_to_obj(cmap, './test.obj')
