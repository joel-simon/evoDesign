import math

class Vector(object):
    def __init__(self, *args):
        """ Create a vector, example: v = Vector(1,2) """
        if len(args)==0: self.values = (0,0)
        else: self.values = args

    def norm(self):
        """ Returns the norm (length, magnitude) of the vector """
        return math.sqrt(sum( comp**2 for comp in self ))

    def copy(self):
        return Vector(*self.values)

    def argument(self):
        """ Returns the argument of the vector, the angle clockwise from +y."""
        arg_in_rad = math.acos(Vector(0,1)*self/self.norm())
        arg_in_deg = math.degrees(arg_in_rad)
        if self.values[0]<0: return 360 - arg_in_deg
        else: return arg_in_deg

    def normalize(self):
        """ Returns a normalized unit vector """
        norm = self.norm()
        if norm == 0.0:
            return 0.0
        normed = tuple( comp/norm for comp in self )
        return Vector(*normed)

    def angle(self, other):
        assert(type(other) == type(self))
        return math.acos(self.inner(other) / (self.norm() * other.norm()) )

    def inner(self, other):
        """ Returns the dot product (inner product) of self and other vector
        """
        return sum(a * b for a, b in zip(self, other))

    def __mul__(self, other):
        """ Returns the dot product of self and other if multiplied
            by another Vector.  If multiplied by an int or float,
            multiplies each component by other.
        """
        if type(other) == type(self):
            return self.inner(other)
        elif type(other) == type(1) or type(other) == type(1.0):
            product = tuple( a * other for a in self )
            return Vector(*product)


    def __rmul__(self, other):
        """ Called if 4*self for instance """
        return self.__mul__(other)

    def __truediv__(self, other):
        # return self.__div__(self, other)
        if type(other) == type(1) or type(other) == type(1.0):
            divided = tuple( a / other for a in self )
            return Vector(*divided)


    def __div__(self, other):
        if type(other) == type(1) or type(other) == type(1.0):
            divided = tuple( a / other for a in self )
            return Vector(*divided)

    def __add__(self, other):
        """ Returns the vector addition of self and other """
        if type(other) == type(1) or type(other) == type(1.0):
            added = tuple( a + other for a in self)
        else:
            added = tuple( a + b for a, b in zip(self, other) )
        return Vector(*added)

    def __sub__(self, other):
        """ Returns the vector difference of self and other """
        if type(other) == type(1) or type(other) == type(1.0):
            subbed = tuple( a - other for a in self)
        else:
            subbed = tuple( a - b for a, b in zip(self, other) )
        return Vector(*subbed)

    def __iter__(self):
        return self.values.__iter__()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __repr__(self):
        return str(self.values)
