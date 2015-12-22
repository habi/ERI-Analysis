# -*- coding: utf-8 -*-

"""
ResolutionPlotter.py | David Haberthür <david.haberthuer@psi.ch>

Script to plot a line through some of the regions of the resolution phantom.
"""

# Imports
import numpy
import os
import glob
import matplotlib.pylab as plt

import lineprofiler


#  Functions
def read_raw(filename, width=2048, height=1024, verbose=False):
    """
    Read the .raw file from the ShadoBox into a numpy array, ready to display
    """
    if verbose:
        print 'Reading image %s' % filename
    # Reading RAW image from the ShadoBox detector. The image is saved as 16
    # bit, with the camera width and height. We swap the endianness of the
    # image to display it nicely.
    image = numpy.fromfile(filename, dtype=numpy.uint16, count=-1).reshape(
        height, width).byteswap()
    # Flip image upside down and left-right, so we can look at it without
    # craning our neck.
    image = numpy.flipud(image)
    return image


def contrast_stretch(image, std=3, verbose=False):
    """
    Clip image histogram to the mean \pm N standard deviations, according to
    http://is.gd/IBV4Gw. I am using three standard deviations around the mean.
    """
    if verbose:
        print 'Clipping image from [' + str(numpy.min(image)) + ':' + \
              str(numpy.max(image)) + '] to',
    clippedimage = numpy.clip(image, numpy.mean(image) - (std * numpy.std(
        image)), numpy.mean(image) + (std * numpy.std(image)))
    if verbose:
        print '[' + str(numpy.min(clippedimage)) + ':' + str(numpy.max(
            clippedimage)) + ']'
    return clippedimage


def display_image_parameters(image, rangecolor='r'):
    """
    Plot the mean +- STD of an image
    """
    plt.axhline(numpy.mean(image), linestyle='-', color=rangecolor, alpha=0.5,
                label='Mean (%0.2f) +- STD' % numpy.mean(image))
    plt.fill_between(range(2048), numpy.mean(image) + numpy.std(image),
                     numpy.mean(image) - numpy.std(image), alpha=0.309,
                     color=rangecolor)


# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=2)
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
UserColors = ["#84DEBD", "#D1B9D4", "#D1D171"]

StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'
FolderList = sorted(os.walk(StartPath).next()[1])

FolderToLookAt = os.path.join(StartPath, FolderList[2])
ImageList = sorted(glob.glob(os.path.join(FolderToLookAt, '*.raw')))

# Prepare figure
plt.ion()
plt.figure(figsize=[20, 9])
plt.suptitle(os.path.basename(FolderToLookAt))

# Grab voltage and current values from all images in folder to plot them
# later on
print 'Reading voltage and current from %s images in folder %s' % (
    len(ImageList), FolderToLookAt)
Voltage = [int(os.path.basename(image).split('_')[1][:-2]) for image in
           ImageList]
Current = [int(os.path.basename(image).split('_')[2][:-2]) for image in
           ImageList]

# Select three lines through resolution phantom
LineYStart = 150
LineLength = 800
Coordinates = [((850, LineYStart), (850, LineYStart + LineLength)),
               ((1150, LineYStart), (1150, LineYStart + LineLength)),
               ((1500, LineYStart), (1500, LineYStart + LineLength))]

# Plot everything
for ImageCounter, ImageName in enumerate(ImageList):
    print '%02d/%s: Reading image and plotting line profile' % (
        ImageCounter + 1, len(ImageList))
    # Which image are we looking at?
    plt.subplot(221)
    plt.cla()
    plt.title('Voltage vs. current')
    plt.scatter(Voltage, Current)
    ThisVoltage = int(os.path.basename(ImageName).split('_')[1][:-2])
    ThisCurrent = int(os.path.basename(ImageName).split('_')[2][:-2])
    plt.plot(ThisVoltage, ThisCurrent, color='red', marker='o', markersize=15,
             alpha=0.309)
    plt.xlabel('Voltage [kV]')
    plt.ylabel('Current [uA]')
    plt.ylim([0, 75])
    # Show the image
    plt.subplot(222)
    plt.cla()
    plt.title('Image %s/%s: %s' % (ImageCounter, len(ImageList),
                                   os.path.basename(ImageName)))
    Img = read_raw(ImageName)
    plt.imshow(contrast_stretch(Img))
    # Show where we select the line profiles
    for CoordinateCounter, CurrentCoordinates in enumerate(Coordinates):
        print CurrentCoordinates
        SelectedPoints, LineProfile = lineprofiler.lineprofile(
            Img, CurrentCoordinates, showimage=False)
        print len(LineProfile)
        plt.plot((SelectedPoints[0][0], SelectedPoints[1][0]),
                 (SelectedPoints[0][1], SelectedPoints[1][1]),
                 color=UserColors[CoordinateCounter], marker='o')
        plt.plot(SelectedPoints[0][0], SelectedPoints[0][1], color='yellow',
                 marker='o')
        plt.plot(SelectedPoints[1][0], SelectedPoints[1][1], color='black',
                 marker='o')
    plt.axis('off')
    # Show the line profiles
    plt.subplot(212)
    plt.cla()
    plt.title('Line profiles')
    for CoordinateCounter, CurrentCoordinates in enumerate(Coordinates):
        SelectedPoints, LineProfile = lineprofiler.lineprofile(
            Img, CurrentCoordinates, showimage=False)
        plt.plot(LineProfile, color=UserColors[CoordinateCounter])
        plt.plot(0, LineProfile[0], color='yellow', marker='o', markersize=15,
                 alpha=0.309)
        plt.plot(len(LineProfile) - 1, LineProfile[-1], color='black',
                 marker='o', markersize=25, alpha=0.309)
    display_image_parameters(Img)
    plt.legend(loc='upper right')
    plt.xlim([0, LineLength])
    plt.ylim([0, 2 ** 12])
    plt.draw()
plt.ioff()
plt.show()
