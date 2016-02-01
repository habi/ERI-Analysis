# -*- coding: utf-8 -*-

"""
ResolutionPlotter.py | David Haberthür <david.haberthuer@psi.ch>

Script to plot a line through some of the regions of the resolution phantom.
"""

# Imports
import os
import glob
import platform
import matplotlib
# Make sure we are running a good version of matplotlib (i.e. > 1)
if float(str(matplotlib.__version__)[:3]) < 1:
    print '\nWe are running matplotlib version', matplotlib.__version__, 'on', \
        platform.node()
    print 'To make this script work, we need a matplotlib version > 1.'
    print 'To load such a version, please enter the following command in', \
        'the terminal and restart the script.'
    print '\n\tmodule load xbl/epd_free/7.3-2-2013.06\n'
    exit()
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle

from ERIfunctions import *


#  Functions
def gaussianfit(data):
    from scipy.optimize import curve_fit

    # Define gaussian model function which we use to calculate a fit to the data
    def gauss(x, *p):
        A, mu, sigma = p
        return A * numpy.exp(-(x - mu) ** 2 / (2. * sigma ** 2))
    # Fit with initial guess p0
    p0 = [50, len(data) / 2, 0.2]
    try:
        # Try to fit a curve, if we fail, then return only zeros
        coeff, var_matrix = curve_fit(gauss, range(0, len(data)), data, p0=p0)
        return gauss(range(0, len(data)), *coeff)
    except RuntimeError:
        return numpy.zeros(len(data))


def LSF(edgespreadfunction):
    return numpy.abs(numpy.diff(edgespreadfunction))


def MTF(linespreadfunction):
    return numpy.abs(numpy.fft.fft(linespreadfunction))[:len(linespreadfunction) / 2]


def normalize(data):
    return (data - numpy.min(data)) / (numpy.max(data) - numpy.min(data))

# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=3)
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
Colors = ["#E9AE70", "#7DDCD8", "#E7B0CF", "#9DE380", "#6CE3AF", "#ABC7E5", "#D8D867", "#B5D79B"]

# Choose the folders we want to compare with each other
StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'
# Filter list for only 'Grid' folders: http://stackoverflow.com/a/4260304
FolderList = [i if 'Grid' in i else '' for i in
              sorted(os.walk(StartPath).next()[1])]
# Filter list to ERI/Hamamatsu
ERIFolders = [i if 'ERI' in i else '' for i in FolderList]
HamamatsuFolders = [i if 'Hamamatsu' in i else '' for i in FolderList]
# Disregard now emtpy list elements: http://stackoverflow.com/a/3845449
ERIFolders = [x for x in ERIFolders if x]
HamamatsuFolders = [x for x in HamamatsuFolders if x]

ChosenERI = ask_user('Which ERI folder shall we use?', ERIFolders)
ChosenHamamatsu = ask_user('Which Hamamatsu folder shall we use to compare with %s?' % bold(ChosenERI), HamamatsuFolders)

# Prepare output directory
OutputPath = os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                          'ERI-Analysis', 'Images', 'Slanted-Edge-Comparison',
                          'Edge-Comparison-' +
                          os.path.basename(ChosenERI) + '_VS_' +
                          os.path.basename(ChosenHamamatsu))
try:
    os.makedirs(OutputPath)
except OSError:
    # Directory already exists
    pass

# Grab necessary values from the images in the two chosen folders
ImageListERI = sorted(glob.glob(os.path.join(StartPath, ChosenERI, '*.raw')))
print 'Reading Parameters from %s images in %s' % (len(ImageListERI),
                                                   bold(ChosenERI))
VoltageERI = [int(os.path.basename(i).split('_')[1][:-2]) for i in ImageListERI]
CurrentERI = [int(os.path.basename(i).split('_')[2][:-2]) for i in ImageListERI]

ImageListHamamatsu = sorted(glob.glob(os.path.join(StartPath, ChosenHamamatsu,
                                                   '*.raw')))
print 'Reading Parameters from %s images in %s' % (len(ImageListERI),
                                                   bold(ChosenHamamatsu))
VoltageHamamatsu = [int(os.path.basename(i).split('_')[1][:-2]) for i in
                    ImageListHamamatsu]
CurrentHamamatsu = [int(os.path.basename(i).split('_')[2][:-2]) for i in
                    ImageListHamamatsu]

# Grab closest values from the Hamamatsu data set and plot them afterwards
CompareImages = []
for c, i in enumerate(ImageListERI):
    # print 80 * '-'
    # print 'Finding best matching current from Hamamatsu for %s (%s kV, ' \
    #       '%s mA)' % (i, VoltageERI[c], CurrentERI[c])
    Candidates = []
    for k in ImageListHamamatsu:
        if str(VoltageERI[c]) + 'kV' in k:
            Candidates.append(k)
    IndexList = [ImageListHamamatsu.index(i) for i in Candidates]
    # Get the closest value to the current from Hamamatsu list. Based on
    # http://stackoverflow.com/a/9706105/323100
    ChosenOne = min(enumerate([CurrentHamamatsu[i] for i in IndexList]),
                    key=lambda x: abs(x[1] - CurrentERI[c]))
    # print 'Found a match in %s' % Candidates[ChosenOne[0]]
    CompareImages.append(Candidates[ChosenOne[0]])
# print 80 * '-'
VoltageMatch = [int(os.path.basename(i).split('_')[1][:-2]) for i in
                CompareImages]
CurrentMatch = [int(os.path.basename(i).split('_')[2][:-2]) for i in
                CompareImages]

# Compare images
plt.ion()
plt.figure(figsize=[20, 9])
for c, i in enumerate(CompareImages):
    plt.clf()
    print '%s/%s | %s kV/%s uA | Comparing %s with %s' % (
        c + 1, len(CompareImages), VoltageERI[c], CurrentERI[c],
        bold(os.path.basename(i)),
        bold(os.path.basename(ImageListERI[c])))
    # Load images
    ImageERI = read_raw(ImageListERI[c])
    ImageHamamatsu = read_raw(i)

    # Crop to interesting region (slanted edge of resolution phantom)
    CropRegion = [100, 900, 575, 675]  # left
    # CropRegion = [100, 900, 1625, 1725]  # right
    CropERI = ImageERI[CropRegion[0]:CropRegion[1], CropRegion[2]:CropRegion[3]]
    CropHamamatsu = ImageHamamatsu[CropRegion[0]:CropRegion[1],
                                   CropRegion[2]:CropRegion[3]]

    # Calculate (average) Edge response
    average = True
    if average:
        ResponseERI = numpy.mean(CropERI, axis=0)
        ResponseHamamatsu = numpy.mean(CropHamamatsu, axis=0)
    else:
        line = 400
        width = 20
        ResponseERI = numpy.mean(CropERI[line - width:line + width, :], axis=0)
        ResponseHamamatsu = numpy.mean(CropHamamatsu[line - width:line + width, :], axis=0)

    # Display images with region of crop
    plt.subplot(251)
    plt.title(os.path.basename(ImageListERI[c]))
    plt.imshow(ImageERI)
    # Draw crop region in original image
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((CropRegion[2], CropRegion[0]),
                                    CropRegion[3] - CropRegion[2],
                                    CropRegion[1] - CropRegion[0], facecolor='red',
                                    edgecolor='w', alpha=0.125))
    plt.subplot(256)
    plt.title(os.path.basename(i))
    plt.imshow(ImageHamamatsu)
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((CropRegion[2], CropRegion[0]),
                                    CropRegion[3] - CropRegion[2],
                                    CropRegion[1] - CropRegion[0], facecolor='red',
                                    edgecolor='w', alpha=0.125))
    # Display cropped region
    plt.subplot(252)
    plt.title('ERI')
    plt.imshow(CropERI)
    plt.subplot(257)
    plt.title('Hamamatsu')
    plt.imshow(CropHamamatsu)
    plt.subplot(153)
    plt.title('Averaged edge response\nwith %s non-averaged overlays' % len(range(100, 800, 200)))
    # Plot some (non-averaged) edge responses, too
    for ctr, line in enumerate(range(100, 800, 200)):
        plt.subplot(252)
        plt.axhline(line, c=Colors[ctr + 2])
        plt.subplot(257)
        plt.axhline(line, c=Colors[ctr + 2])
        plt.subplot(153)
        plt.plot(CropERI[line, :], alpha=0.618, c=Colors[ctr + 2], linewidth=1)
        plt.plot(CropHamamatsu[line, :], alpha=0.618, c=Colors[ctr + 2], linewidth=1)
    plt.plot(ResponseERI, c=Colors[0], label='ERI')
    plt.plot(ResponseHamamatsu, c=Colors[1], label='Hamamatsu')
    plt.ylim(0, 2 ** 12)
    plt.legend(loc='best')

    # Calculate MTF.
    # According to http://www.imatest.com/docs/validating_slanted_edge/, the MTF is
    # the Fourier transform of the line spread function, which is the derivative of
    # the averaged edge.
    # We thus calculate the average edge ($source$Response) and take the derivative
    # of this (with the `LSF` function, which uses `numpy.diff`).
    # To the derivative we fit a gaussian function with the `gaussianfit` function
    # which then acts as an input for the `MTF` function above.
    plt.subplot(154)
    plt.title('Line spread function')
    plt.plot(LSF(ResponseERI), c=Colors[2], linestyle='dashed', label='ERI Data')
    plt.plot(LSF(ResponseHamamatsu), c=Colors[3], linestyle='dashed', label='Hamamatsu Data')
    plt.plot(gaussianfit(LSF(ResponseERI)), c=Colors[0], label='ERI fit')
    plt.plot(gaussianfit(LSF(ResponseHamamatsu)), c=Colors[1], label='Hamamatsu fit')
    plt.legend(loc='best')
    plt.subplot(155)
    plt.title('MTF')
    plt.plot(normalize(MTF(gaussianfit(LSF(ResponseERI)))), c=Colors[0],
             label='MTF ERI')
    plt.plot(normalize(MTF(gaussianfit(LSF(ResponseHamamatsu)))), c=Colors[1],
             label='MTF Hamamatsu')
    plt.legend(loc='best')
    # Save figure and concatenated results
    plt.savefig(os.path.join(OutputPath, 'MTF%03dkV%03duA.png' % (VoltageERI[c], CurrentERI[c])))
    plt.draw()
    plt.pause(0.01)
plt.ioff()
plt.show()
