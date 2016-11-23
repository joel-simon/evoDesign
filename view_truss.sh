#!/usr/bin/env pypy

import argparse

from src.views.viewer import Viewer
from src.modules.truss.truss import Truss
from src.modules.truss.draw import draw_truss

def main(args):
    truss = Truss(args.path)
    truss.calc_fos()
    viewer = Viewer(bounds=(8, 8, 8))
    draw_truss(viewer, truss)
    print(('#'*34)+' View Truss '+('#'*34))
    print('file = %s' % args.path)
    print('mass = %f' % truss.mass)
    print('fos = %f' % truss.fos_total)
    print('num joints = %i' % len(truss.joints))
    print('num members = %i' % len(truss.members))
    viewer.main_loop()
    print('#'*80)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='Full path to .trs file.')
    args = parser.parse_args()
    main(args)
