import numpy

class Joint(object):

    def __init__(self, coordinates, translation):
        # Save the joint id
        self.idx = -1

        # Coordinates of the joint
        self.coordinates = coordinates

        # Allowed translation in x, y, and z
        self.translation = numpy.array([translation]).T# numpy.ones([3, 1])
        assert(self.translation.shape == (3, 1))
        
        # Loads
        self.loads = numpy.zeros([3, 1])

        # Store connected members
        self.members = []

        # Reactions
        self.reactions = numpy.zeros([3, 1])

        # Deflections
        self.deflections = numpy.zeros([3, 1])

        self.userData = dict()