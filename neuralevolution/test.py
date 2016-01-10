import numpy as np
import matplotlib.pyplot as plt
np.set_printoptions(linewidth=125, precision=2, suppress=True)

def makeGaussian(size, fwhm = 3, center=None):
  """ Make a square gaussian kernel.
  size is the length of a side of the square
  fwhm is full-width-half-maximum, which
  can be thought of as an effective radius.
  """
  x = np.arange(0, size, 1, float)
  y = np.arange(0, size, 1, float)[:,np.newaxis]
  if center is None:
    x0 = y0 = size // 2
  else:
    x0 = center[0]
    y0 = center[1]

  print(((x-x0)**2 + ((y)-y0)**2))
  derp = -4*np.log(2) * ((x-x0)**2 + ((y)-y0)**2) / fwhm**2
  return np.exp(derp)


# gaus = makeGaussian(5)
# print(gaus)

size_x = 5
size_y = 8
x = np.arange(0, size_x, 1, float)
y = np.arange(0, size_y, 1, float)[:,np.newaxis]
x0 = size_x // 2
y0 = size_y // 2

print(((x-x0)**2 + ((y)-y0)**2))