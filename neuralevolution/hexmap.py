import math
import pygame
import random
import numpy as np

SQRT3 = math.sqrt( 3 )

class Map( object ):
	"""
	An top level object for managing all game data related to positioning.
	"""
	directions = [ ( 0, 1 ), ( 1, 1 ), ( 1, 0 ), ( 0, -1 ), ( -1, -1 ), ( -1, 0 ) ]

	def __init__( self, rows, cols, *args, **keywords ):
		#Map size
		self.rows = rows
		self.cols = cols
		self.values = np.zeros([rows,cols]).astype(bool)

	def __str__( self ):
		return "Map (%d, %d)" % ( self.rows, self.cols )

	@property
	def size( self ):
		"""Returns the size of the grid as a tuple (row, col)"""
		return ( self.rows, self.cols )

	def distance( self, start, destination ):
		"""Takes two hex coordinates and determine the distance between them."""
		logger.debug( "Start: %s, Dest: %s", start, destination )
		diffX = destination[0] - start[0]
		diffY = destination[1] - start[1]

		distance = min( abs( diffX ), abs( diffY ) ) + abs( diffX - diffY )

		logger.debug( "diffX: %d, diffY: %d, distance: %d", diffX, diffY, distance )
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
			text_length = 3

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
					text = "%d,%d" % ( row + col / 2, col ) if numbers else ""
					top 	 += ( text ).center( text_length ) + "\\"
					bottom	 += ( "" ).center( text_length, '_' ) + "/"
				else:
					text = "%d,%d" % ( 1 + row + col / 2, col ) if numbers else " "
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

	def valid_cell( self, cell ):
		row, col = cell
		if col < 0 or col >= self.cols: return False
		if row < math.ceil( col / 2.0 ) or row >= math.ceil( col / 2.0 ) + self.rows: return False
		return True

	def neighbors( self, center ):
		"""
		Return the valid cells neighboring the provided cell.
		"""
		return filter( self.valid_cell, [
			( center[0] - 1, center[1] ), ( center[0], center[1] + 1 ),
			( center[0] + 1, center[1] + 1 ), ( center[0] + 1, center[1] ),
			( center[0], center[1] - 1 ), ( center[0] - 1, center[1] - 1 )
		] )

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

def draw_map(screen, m, radius):
	hex_coords = [( .5 * radius, 0 ),
			( 1.5 * radius, 0 ),
			( 2 * radius, SQRT3 / 2 * radius ),
			( 1.5 * radius, SQRT3 * radius ),
			( .5 * radius, SQRT3 * radius ),
			( 0, SQRT3 / 2 * radius )
	]
	# A point list describing a single cell, based on the radius of each hex
	for col in range( m.cols ):
		offset = radius * SQRT3 / 2 if col % 2 else 0
		for row in range( m.rows ):
			# Calculate the offset of the cell
			top = offset + SQRT3 * row * radius
			left = 1.5 * col * radius
			# Create a point list containing the offset cell
			points = [( x + left, y + top ) for ( x, y ) in hex_coords]
			color = (0,0,0)
			if m.values[row, col]:
				color = (0, 200, 0)
			pygame.draw.polygon( screen, color, points)
