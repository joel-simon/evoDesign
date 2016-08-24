from .drawUtils import draw_polygon, draw_circle, draw_line, xy_to_screen, draw_text

BLACK = (0,0,0)
GRAY = (100,100,100)
WHITE = (255,255,255)
LIGHT_GREEN = (0, 200, 0, 10)
SQRT3 = 1.73050808

class HexArtist(object):
    def __init__(self, surface, radius):
        self.surface = surface
        self.points = None
        self.radius = radius

    def set_hex(self, coord):
        self.points = self.hex_points(coord[0], coord[1])

    def fill(self, color):
        assert self.points
        draw_polygon(self.surface, self.points, color)

    def border(self, color=BLACK, width=1):
        assert self.points
        draw_polygon(self.surface, self.points, color, width)

    def text(self, string, color=BLACK):
        p = (self.center[0] + 7, self.center[1]-20)
        draw_text(self.surface, p, string, color)

    def hex_points(self, row, col):
        radius = self.radius
        surface = self.surface
        offset = radius * SQRT3 / 2 if col % 2 else 0
        top = offset + SQRT3 * row * radius
        left = 1.5 * col * radius

        self.center = xy_to_screen(int(left), int(top), self.surface)

        hex_coords = [( .5 * radius, 0 ),
            ( 1.5 * radius, 0 ),
            ( 2 * radius, SQRT3 / 2 * radius ),
            ( 1.5 * radius, SQRT3 * radius ),
            ( .5 * radius, SQRT3 * radius ),
            ( 0, SQRT3 / 2 * radius ),
            ( .5 * radius, 0 )
        ]
        points = []

        for x, y in hex_coords:
            points.append(xy_to_screen(int(x + left), int( y + top), surface))

        return points

# def hex_color(row, col, hmap):
#     if hmap[row][col]:
#         return GRAY
#     else:
#         return WHITE

def draw_hex_map(surface, hmap, draw_func):
    # TODO calculate radius by surface dimensions and map size
    artist = HexArtist(surface, radius=14./1)
    for coord in hmap.coords():
        artist.set_hex(coord)
        draw_func(coord, artist)

            # points = hex_points(row, col, radius, surface)
            # # color = color_func(row, col, hmap)

            # draw_polygon(surface, points, color)
            # draw_polygon(surface, points, (20, 20, 20),  1)

