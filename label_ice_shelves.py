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

def label_ice_shelves(mask):
    mask_grounded = 1
    mask_floating = 2

    nrows,ncols = mask.shape

    # identify "ice rises"
    mask1 = np.zeros_like(mask)
    mask1[mask == mask_grounded] = 2
    mask1[nrows/2,ncols/2] = 1

    # in continent "ice rises" are 1, everything else is zero
    continent = cc.cc(mask1, True)
    # incorporate the continental ice sheet in continent
    continent[mask == mask_grounded] += 1

    # create a mask with ice shelves connected by "ice rises"
    mask2 = np.zeros_like(mask)
    mask2[mask == mask_floating] = 1
    mask2[continent == 2] = 1

    # label ice shelves
    shelves = cc.cc(mask2, False)

    # remove ice rises from ice shelves
    shelves[continent == 2] = 0

    return continent, shelves

def relabel(mask):

    nrows, ncols = mask.shape

    labels = {}
    for r in range(nrows):
        for c in range(ncols):

            blob = mask[r, c]

            try:
                label = labels[blob]
            except KeyError:
                label = r * nrows + c

            labels[blob] = label

            mask[r, c] = label

    return mask

continent, shelves = label_ice_shelves(mask)

new_shelves = relabel(shelves.copy())

cmap = plt.cm.Blues

plt.figure()
plt.imshow(np.flipud(continent), interpolation='nearest', cmap=cmap)
plt.title("Continental ice shelf and Ice 'rises'")

plt.figure()
plt.imshow(np.flipud(shelves), interpolation='nearest', cmap=cmap)
plt.title("Ice shelves, labeled")

plt.figure()
plt.imshow(np.flipud(new_shelves), interpolation='nearest', cmap=cmap)
plt.title("Ice shelves, relabeled")

plt.show()
