"""
Wattage.py | David Haberthuer <david.haberthuer@psi.ch>

Quickly calculate the output power of the ERI source for all experiments
"""

import os
import glob
import matplotlib.pylab as plt
import numpy
import scipy.optimize
import scipy.stats

from ERIfunctions import *

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ERIFolders = sorted(glob.glob(os.path.join(StartPath, 'ERI*')))


# Grab all images and plot values for folders
ImageList = []
AllImages = []
for counter, folder in enumerate(ERIFolders):
    print 'Reading kV and uA values from folder %s/%s: %s' % (counter + 1,
                                                              len(ERIFolders),
                                                              os.path.basename(folder))
    ImageList = sorted(glob.glob(os.path.join(StartPath, folder, '*.raw')))
    AllImages += ImageList
Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                       image in AllImages])
Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                       image in AllImages])
Watt = Voltage * 1e3 * Current * 1e-6

print
print 'We have a maximal output power of %s W (at %s kV/ %s uA) for %s in %s' % (
    max(Watt), Voltage[Watt.argmax()], Current[Watt.argmax()],
    bold(os.path.basename(AllImages[Watt.argmax()])),
    bold(os.path.basename(os.path.dirname(AllImages[Watt.argmax()]))))
print 'We have a minimal output power of %s W (at %s kV/ %s uA) for %s in %s' % (
    min(Watt), Voltage[Watt.argmin()], Current[Watt.argmin()],
    bold(os.path.basename(AllImages[Watt.argmin()])),
    bold(os.path.basename(os.path.dirname(AllImages[Watt.argmin()]))))
