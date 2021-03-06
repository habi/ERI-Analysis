# -*- coding: utf-8 -*-

"""
ResolutionPlotter.py | David Haberthür <david.haberthuer@psi.ch>

Script to plot a line through some of the regions of the resolution phantom.
"""

import numpy
import os
import glob
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle

import lineprofiler
from ERIfunctions import *

# Colors from 'I want hue'
UserColors = ["#84DEBD", "#D1B9D4", "#D1D171"]

StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'
# Only do 'Grid' Folders
FolderList = [i if 'Grid' in i else '' for i in sorted(os.walk(StartPath).next()[1])]
# Disregard now emtpy list elements: http://stackoverflow.com/a/3845449
FolderList = [x for x in FolderList if x]
for Folder in FolderList:
    FolderToLookAt = os.path.join(StartPath, Folder)
    ImageList = sorted(glob.glob(os.path.join(FolderToLookAt, '*.raw')))

    # Prepare output directory
    try:
        os.makedirs(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                                 'ERI-Analysis', 'Images',
                                 'Resolution-' +
                                 os.path.basename(FolderToLookAt)))
    except OSError:
        # Directory already exists
        pass

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
    LineYStart = 100
    LineLength = 850
    Coordinates = [((850, LineYStart), (850, LineYStart + LineLength)),
                   ((1150, LineYStart), (1150, LineYStart + LineLength)),
                   ((1500, LineYStart), (1500, LineYStart + LineLength))]
    # Plot everything
    for ImageCounter, ImageName in enumerate(ImageList):
        print '%02d/%s: Reading image %s and plotting line profiles' % (
            ImageCounter + 1, len(ImageList), os.path.basename(ImageName))
        ThisVoltage = int(os.path.basename(ImageName).split('_')[1][:-2])
        ThisCurrent = int(os.path.basename(ImageName).split('_')[2][:-2])
        # Only do the thing if the current is not larger than the exponential
        # fit that we found with VoltageVsCurrentExponentialFit.py, which is
        # 1.05e-01 * numpy.exp(9.04e-02 * x) + 8.72e+00 (and a safety margin).
        # Or the voltage is not larger than 66 keV
        if ThisCurrent < 1.05e-1 * numpy.exp(9.04e-2 * ThisVoltage) + 20 and \
                ThisVoltage < 66:
            # Which image are we looking at from all the ones recorded?
            plt.subplot(421)
            plt.cla()
            plt.title('Voltage vs. current')
            plt.scatter(Voltage, Current)
            plt.plot(ThisVoltage, ThisCurrent, color='red', marker='o',
                     markersize=15, alpha=0.309)
            plt.xlabel('Voltage [kV]')
            plt.ylabel('Current [uA]')
            plt.xlim([20, 70])
            plt.ylim([0, 75])
            # Show the current image
            plt.subplot(422)
            plt.cla()
            plt.title('Contrast stretched Image %s/%s: %s\nWith line profiles '
                      'and red region used for mean and STD' % (
                          ImageCounter + 1, len(ImageList),
                          os.path.basename(ImageName)))
            Img = read_raw(ImageName)
            plt.imshow(contrast_stretch(Img))
            # Show where line profiles have been calculated
            for CoordinateCounter, CurrentCoordinates in enumerate(Coordinates):
                SelectedPoints, LineProfile = lineprofiler.lineprofile(
                    Img, CurrentCoordinates, showimage=False)
                plt.plot((SelectedPoints[0][0], SelectedPoints[1][0]),
                         (SelectedPoints[0][1], SelectedPoints[1][1]),
                         color=UserColors[CoordinateCounter], marker='o')
                plt.plot(SelectedPoints[0][0], SelectedPoints[0][1],
                         color='yellow', marker='o', alpha=0.618)
                plt.plot(SelectedPoints[1][0], SelectedPoints[1][1],
                         color='black', marker='o', alpha=0.618)
            plt.axis('off')
            # Crop region for Standard deviation
            CropSize = 900
            CropStart = [50, 700]
            Crop = Img[CropStart[0]:CropStart[0] + CropSize,
                       CropStart[1]:CropStart[1] + CropSize]
            # Draw crop region in original image
            currentAxis = plt.gca()
            currentAxis.add_patch(Rectangle((CropStart[1], CropStart[0]),
                                            CropSize, CropSize, facecolor='red',
                                            edgecolor='w', alpha=0.125))
            # Show the line profiles
            for CoordinateCounter, CurrentCoordinates in enumerate(Coordinates):
                plt.subplot(5, 1, 3 + CoordinateCounter)
                plt.cla()
                if not CoordinateCounter:
                    # Title the first of the three line plots
                    plt.title('Red = mean (%0.2f) +- STD of cropped region, '
                              'grey = mean +- 2 x STD.)' % numpy.mean(Crop))
                if 'Grid' in os.path.basename(FolderToLookAt):
                    xStart = 240
                    xShift = 320
                    yStart = numpy.mean(Crop) + 150
                    if CoordinateCounter == 2:
                        # Annotate first line profile if we have imaged the grid
                        plt.annotate('2.8 lp/mm', xy=(xStart + 1 * xShift, yStart))
                        plt.annotate('2.5 lp/mm', xy=(xStart + 2 * xShift, yStart))
                        plt.annotate('2.2 lp/mm', xy=(xStart + 3 * xShift, yStart))
                        plt.annotate('2.0 lp/mm', xy=(xStart + 4 * xShift, yStart))
                    elif CoordinateCounter == 1:
                        # Annotate second line profile
                        plt.annotate('4.3 lp/mm', xy=(xStart, yStart))
                        plt.annotate('4.0 lp/mm', xy=(xStart + 1 * xShift, yStart))
                        plt.annotate('3.7 lp/mm', xy=(xStart + 2 * xShift, yStart))
                        plt.annotate('3.4 lp/mm', xy=(xStart + 3 * xShift, yStart))
                        plt.annotate('3.1 lp/mm', xy=(xStart + 4 * xShift, yStart))
                    else:
                        # Annotate third line profile
                        plt.annotate('6.0 lp/mm', xy=(xStart, yStart))
                        plt.annotate('5.6 lp/mm', xy=(xStart + 1 * xShift, yStart))
                        plt.annotate('5.3 lp/mm', xy=(xStart + 2 * xShift, yStart))
                        plt.annotate('5.0 lp/mm', xy=(xStart + 3 * xShift, yStart))
                        plt.annotate('4.6 lp/mm', xy=(xStart + 4 * xShift, yStart))
                # Gray region to 2xSTD
                plt.fill_between(range(2048),
                                 numpy.mean(Crop) + 2 * numpy.std(Crop),
                                 numpy.mean(Crop) - 2 * numpy.std(Crop),
                                 color='k', alpha=0.5, linewidth=1)
                # Red region to 2xSTD
                plt.fill_between(range(2048),
                                 numpy.mean(Crop) + numpy.std(Crop),
                                 numpy.mean(Crop) - numpy.std(Crop),
                                 color='r', linewidth=1)
                # Plot mean and STD of cropped region
                plt.axhline(numpy.mean(Crop), linestyle='-',
                            color='k', linewidth=1)
                SelectedPoints, LineProfile = lineprofiler.lineprofile(
                    Img, CurrentCoordinates, showimage=False)
                plt.plot(LineProfile, color=UserColors[CoordinateCounter])
                plt.xlim([0, len(LineProfile)])
                plt.ylim([0, 2 ** 12])
                plt.plot(0, numpy.mean(Crop), color='yellow', marker='o',
                         markersize=15, alpha=0.618)
                plt.plot(len(LineProfile) - 1, numpy.mean(Crop), color='black',
                         marker='o', markersize=15, alpha=0.618)
                plt.xlim([0, len(LineProfile)])
                plt.ylim([0, 2 ** 12])
            plt.draw()
            plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                                     'ERI-Analysis', 'Images',
                                     'Resolution-' + os.path.basename(FolderToLookAt),
                                     os.path.splitext(os.path.basename(ImageName))[0] + '.png'))
        else:
            print '\tThe current of %s uA is larger than the fit of %0.2f uA, ' \
                  'or the voltage is later than 65 keV thus not looking at ' \
                  'the image' % (ThisCurrent,
                                 ThisVoltage * 0.1 * numpy.exp(9.04e-2) + 10)
    plt.ioff()
    plt.close('all')
