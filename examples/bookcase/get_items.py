import numpy as np

def get_items(area, cell_width):
    """ Create a random distribution of book dimensions.
    """
    # Common book sizes in meters. 
    book_sizes = {
        'folio': (.305, .48),
        'quarto': (.24, .305),
        'imperial_octavo': (.2, .29),
        'super_octavo': (.18, .28),
        'royal_octavo': (.165, .25),
        'medium_octavo': (.165, .235),
        'octavo': (.15, .23),
        'crown_octavo': (.135, .2),
        'duodecimo': (.125, .19),
        'sextodecimo': (.1, .17),
        'octodecimo': (.1, .165)
    }
    # Book sizes in cell units
    cell_sizes = [(int(y/cell_width), int(x/cell_width)) \
                                            for k, (x,y) in book_sizes.items()]
    a = 0
    items = []
    while a < area:
        idx = int(round(np.random.normal(len(cell_sizes)/2, scale=2)))
        idx = min(len(cell_sizes)-1, max(0, idx))
        items.append(cell_sizes[idx])
        a += items[-1][0]# * items[-1][0]

    return items

get_items(1000, 1/20.)