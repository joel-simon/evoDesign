import math
import random
import numpy as np

SQRT3 = math.sqrt( 3 )

from functools import partial

class memoize(object):
  """cache the return value of a method
  
  This class is meant to be used as a decorator of methods. The return value
  from a given method invocation will be cached on the instance whose method
  was invoked. All arguments passed to a method decorated with memoize must
  be hashable.
  
  If a memoized method is invoked directly on its class the result will not
  be cached. Instead the method will be invoked like a static method:
  class Obj(object):
      @memoize
      def add_to(self, arg):
          return self + arg
  Obj.add_to(1) # not enough arguments
  Obj.add_to(1, 2) # returns 3, result is not cached
  """
  def __init__(self, func):
    self.func = func
  def __get__(self, obj, objtype=None):
    if obj is None:
        return self.func
    return partial(self, obj)
  def __call__(self, *args, **kw):
    obj = args[0]
    try:
        cache = obj.__cache
    except AttributeError:
        cache = obj.__cache = {}
    key = (self.func, args[1:], frozenset(kw.items()))
    try:
        res = cache[key]
    except KeyError:
        res = cache[key] = self.func(*args, **kw)
    return res



class Map( object ):
	"""
	An top level object for managing all game data related to positioning.
	"""
	# directions = [ ( 0, 1 ), ( 1, 1 ), ( 1, 0 ), ( 0, -1 ), ( -1, -1 ), ( -1, 0 ) ]

	def __init__( self, shape, dtype=float, *args, **keywords ):
		#Map size
		self.rows = shape[0]
		self.cols = shape[1]
		self.values = np.zeros(shape).astype(dtype)

	def __str__( self ):
		return self.ascii(False)
		# return str(self.values)
		# return "Map (%d, %d)" % ( self.rows, self.cols )

	@property
	def size( self ):
		"""Returns the size of the grid as a tuple (row, col)"""
		return ( self.rows, self.cols )

	def distance( self, start, destination ):
		"""Takes two hex coordinates and determine the distance between them."""
		# logger.debug( "Start: %s, Dest: %s", start, destination )
		diffX = destination[0] - start[0]
		diffY = destination[1] - start[1]

		distance = min( abs( diffX ), abs( diffY ) ) + abs( diffX - diffY )

		# logger.debug( "diffX: %d, diffY: %d, distance: %d", diffX, diffY, distance )
		return distance

	def ascii( self, numbers=True ):
		""" Debug method that draws the grid using ascii text """

		table = ""

		if numbers:
			text_length = len( 
				str( self.rows - 1 if self.cols % 2 == 1 else self.rows ) +
				',' +
				str( int( self.rows - 1 + math.floor( self.cols / 2 ) ) )
			)
		else:
			text_length = 2

		#Header for first row
		for col in range( self.cols ):
			if col % 2 == 0:
				table += " " + '_' * text_length
			else:
				table += " " + ' ' * text_length
		table += "\n"
		# Each row
		for row in range( self.rows ):
			top = "/"
			bottom = "\\"

			for col in range( self.cols ):
				if col % 2 == 0:
					text = "%d,%d" % (row, col ) if numbers else str(self.values[row, col])
					top 	 += ( text ).center( text_length ) + "\\"
					bottom += ( "" ).center( text_length, '_' ) + "/"
				else:
					text = "%d,%d" % (row, col ) if numbers else str(self.values[row, col])
					top 	 += ( "" ).center( text_length, '_' ) + "/"
					bottom	 += ( text ).center( text_length ) + "\\"
			# Clean up tail slashes on even numbers of columns
			if self.cols % 2 == 0:
				if row == 0: top = top[:-1]
			table += top + "\n" + bottom + "\n"

		# Footer for last row
		footer = " "
		for col in range( 0, self.cols - 1, 2 ):
			footer += " " * text_length + "\\" + '_' * text_length + "/"
		table += footer + "\n"
		return table

	def directions(self, position):
		# for a hex in an odd column	
		directions_odd = [(-1, 0), (0,1), (1,1), (1,0), (1, -1), (0,-1)]
		# for a hex in an even column
		directions_even = [(-1, 0), (-1, 1), (0,1), (1,0), (0, -1), (-1,-1)]
		return directions_even if position[1] % 2 == 0 else directions_odd

	def valid_cell( self, cell ):
		row, col = cell
		if col < 0 or col >= self.cols: return False
		if row < 0 or row >= self.rows: return False
		return True

	@memoize
	def neighbors( self, center ):
		"""
		Return the valid cells neighboring the provided cell.
		"""
		neighbors = [ (center[0] +a, center[1] + b) for a, b in self.directions(center)]
		return list(filter( self.valid_cell, neighbors ))

	def is_occupied(self, coords):
		if (self.valid_cell(coords) and self.values[coords] > 0):
			return coords
		else:
			return False

	def occupied_neighbors(self, center):
		assert(len(center) == 2)
		neighbors = [ (center[0] +a, center[1] + b) for a, b in self.directions(center)]
		return map( self.is_occupied, neighbors)

	def num_occupied_neighbors(self, center):
		n = 0
		for a, b in self.directions(center):
			if self.is_occupied((center[0] + a, center[1] + b)):
				n += 1
		return n

	@memoize
	def spread( self, center, radius=1 ):
		"""
		A slice of a map is a collection of valid cells, starting at an origin, 
		and encompassing all cells within a given radius. 
		"""
		result = set( ( center, ) )				#Start out with this center cell
		neighbors = self.neighbors( center )	#Get the neighbors for use later
		if radius == 1:							#Recursion end case
			result = result | set( neighbors )	#Return the set of this cell and its neighbors
		else:					#Otherwise, recurse over all the neghbors, 
			for n in neighbors:	#decrementing the radius by one.
				result = result | set( self.spread( n, radius - 1 ) )
		return filter( self.valid_cell, result )#filter invalid cells before returning.

	def line( self, origin, direction, length=3 ):
		"""
		Returns all the cells along a given line, starting at an origin
		"""
		offset = self.directions[direction]
		results = [ origin ]
		# Work each row, i units out along an edge
		for i in range( 1, length + 1 ):
			results.append( ( origin[0] + offset[0] * i, origin[1] + offset[1] * i ) )
		return filter( self.valid_cell, results )

	def add(coords, value):
		pass

	def filter_unconnected(self, front = set()):

		# front = set([(0, c) for c, v in enumerate(self.values[0]) if v > 0 and c %2 == 0])
		seen = set()
		
		filtered_values = np.empty_like(self.values)

		while len(front) > 0:
			next_front = set()
			for (i, j) in front:
				filtered_values[i, j] = 1#self.values[i, j]
				foo = [on for on in self.occupied_neighbors((i, j)) if on != False ]
				next_front.update(foo)

			seen.update(front)
			next_front = next_front.difference(seen)
			front      = next_front

		self.values = filtered_values
		return self


if __name__ == '__main__':
	hex_map = Map((8,8,), int)
	print(hex_map)