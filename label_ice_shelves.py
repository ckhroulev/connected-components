#!/usr/bin/env python

import cc
import netCDF4 as NC
import numpy as np
import pylab as plt
import argparse

parser = argparse.ArgumentParser()
parser.description = "Identify icebergs using a PISM-style mask read from a file."
parser.add_argument("FILE", nargs=1)
options = parser.parse_args()

nc = NC.Dataset(options.FILE[0])

mask = np.squeeze(nc.variables['mask'][:])
mask_grounded = 1
mask_floating = 2

nrows,ncols = mask.shape

# identify "ice rises"
mask1 = np.zeros_like(mask)
mask1[mask == mask_grounded] = 2
mask1[nrows/2,ncols/2] = 1

# in result "ice rises" are 1, everything else is zero
result = cc.cc(mask1, True)
# incorporate the continental ice sheet in result
result[mask == mask_grounded] += 1

# create a mask with ice shelves connected by "ice rises"
mask2 = np.zeros_like(mask)
mask2[mask == mask_floating] = 1
mask2[result == 2] = 1

# label ice shelves
result2 = cc.cc(mask2, False)

# remove ice rises from ice shelves
result2[result == 2] = 0

plt.figure()
plt.imshow(np.flipud(result), interpolation='nearest')
plt.title("Continental ice shelf and Ice 'rises'")

plt.figure()
plt.imshow(np.flipud(result2), interpolation='nearest')
plt.title("Ice shelves, labeled")

plt.show()
