#!/bin/bash
pypy -m cppn.main
python cppn/generate_out.py
pypy -m cppn.view
