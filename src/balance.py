import math
from src.map_utils import shape, empty

def point_line_dist(x, y, x1, y1, x2, y2):
    """ Minimum distance between a point (x,y) and a line segment (x1, y1), (x2, y2).
    """
    A = x - x1
    B = y - y1
    C = x2 - x1
    D = y2 - y1

    dot = A * C + B * D
    len_sq = C * C + D * D
    param = -1

    if (len_sq != 0): #in case of 0 length line
        param = dot / len_sq

    xx, yy = 0,0

    if (param < 0):
        xx = x1
        yy = y1
    elif (param > 1):
        xx = x2
        yy = y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D

    dx = x - xx
    dy = y - yy
    return math.sqrt(dx * dx + dy * dy)

def point_polygon_distance(x, y, verts):
    """ Minimum distance between a point and a polygon.
        return distance and the segment.
    """
    # minimum of ditance bwtween point and each edge.
    d = None
    segment = None
    for i in range(len(verts)):
        x1, y1 = verts[i]
        x2, y2 = verts[i-1]
        d2 = point_line_dist(x, y, x1, y1, x2, y2)
        if d==None or d2 < d:
            d = d2
            segment = (x1, y1, x2, y2)
    return d, segment

def polygon_center(points):
    cx, cy = 0., 0.
    for x, y in points:
        cx += x
        cy += y
    cx /= len(points)
    cy /= len(points)
    return cx, cy

def polygon_area(points):
    """ points must be ordered in clockwise or counter-clockwise direction
    """
    n = len(points) # of points
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    area = abs(area) / 2.0
    return area

def average_radius(points):
    cx, cy = 0., 0.
    for x, y in points:
        cx += x
        cy += y
    cx /= len(points)
    cy /= len(points)
    r = 0.0
    for x, y in points:
        r += abs(x-cx + y-cy)
    return r / float(len(points))

def distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside =False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def balance_score2(cells, verbose=False):
    """ Given a 3 dimensional list of points return a balance score in [0, 1].
        The balance score is based on the distance from the center of mass
        to the nearest nearest edge of the convex hull of bottom points.

        com = center of mass of objects(y>0).
        cv = convex hull of objects(y==0).

        d = shortest distance from com to cv in xz plane.

    """

    if len(cells) == 0:
        return 0

    com = [0, 0, 0] # Store center of mass for all points.
    bottom_points = [] # Store all points on bottom as (x, z) tuples.
    # n = 0

    for cell in cells:
        x, y, z = cell.position
        if y == 0:
            bottom_points.append((x-.5, z-.5))
            bottom_points.append((x+.5, z-.5))
            bottom_points.append((x-.5, z+.5))
            bottom_points.append((x+.5, z+.5))
        com[0] += x
        com[1] += y
        com[2] += z

    com[0] /= float(len(cells))
    com[1] /= float(len(cells))
    com[2] /= float(len(cells))

    # The map should be fully connected.
    if len(bottom_points) == 0:
        return 0

    # all in the xz plane
    bottom_hull = convex_hull(bottom_points)
    bottom_area = polygon_area(bottom_hull)
    bottom_center = polygon_center(bottom_hull)
    bottom_radius = average_radius(bottom_hull)

    # Get the segment of the convex hull, closest to xz component of center of mass
    # d, segment = point_polygon_distance(com[0], com[2], bottom_hull)
    # Get distance between center of convex hull and that segment
    # D = point_line_dist(*bottom_center, *segment)
    # bottom_radius = max(1, 0)
    x = distance((com[0], com[2]), bottom_center) / bottom_radius

    if verbose:
        print('com', com)
        print('bottom_area', bottom_area)
        print('bottom_hull', bottom_hull)
        # print('bottom_radius', bottom_radius)
        # print('d',d)
        # print('D',D)
        print('x=',x)
        print('foo', (1 if com[1]==0 else min(1, bottom_area/com[1])))
    score = math.exp(-2*x**2) * (1 if com[1]==0 else min(1, bottom_area/com[1]))

    return score

def balance_score(cells, cmap, verbose=False):
    if len(cells) == 0:
        return 0

    X, Y, Z = shape(cmap)
    bottom_points = [] # Store all points on bottom as (x, z) tuples.

    # Create lsit of all points touching the bottom.
    for x in range(X):
        for z in range(Z):
            if cmap[x][0][z]:
                bottom_points.append((x-.5, z-.5))
                bottom_points.append((x+.5, z-.5))
                bottom_points.append((x-.5, z+.5))
                bottom_points.append((x+.5, z+.5))

    if len(bottom_points) == 0:  # The map should be fully connected.
        return 0

    # Create the convex hull of bottom points, this is the 'base'
    bottom_hull = convex_hull(bottom_points)

    # Store which XZ coordiantes lie in the base.
    in_hull_map = empty((X, Z))
    for x in range(X):
        for z in range(Z):
            if point_inside_polygon(x, z, bottom_hull):
                in_hull_map[x][z] = 1

    # Count what percent of mass is in the base on the XZ plane
    in_hull = 0
    for cell in cells:
        x, _, z = cell.position
        if in_hull_map[x][z]:
            in_hull += 1

    # TODO: multiply by max(1, shortest width / COM_height)
    return in_hull/ float(len(cells))


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """

    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list.
    return lower[:-1] + upper[:-1]
