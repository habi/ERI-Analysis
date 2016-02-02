# -*- coding: utf-8 -*-

"""
BrightnessComparison | David Haberthür <david.haberthuer@psi.ch>

Script to get compare the brightness of the images from ERI and
Hamamatsu
"""

# Imports
import os
import glob
import matplotlib.pylab as plt
from matplotlib.patches import Rectangle

from ERIfunctions import *

# Reset markers from standard
#~ plt.rc('lines', linewidth=2, marker='o')
# Colors from 'I want hue'
colors = ["#B2E183", "#D3B8D8", "#80DCCB", "#E5BC6E"]

Ubuntu = True
if Ubuntu:
    StartPath = '/afs/psi.ch/user/h/haberthuer/slsbl/x02da/e13960/Data20/Gantry/Images'
else:
    StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'

# Filter list for only 'Grid' folders: http://stackoverflow.com/a/4260304
FolderList = sorted(os.walk(StartPath).next()[1])
# Filter list to remove the folders to disregard
FolderList = [i if 'DoNotUse' not in i else '' for i in FolderList]
# Only show these folders (Wrench, Grid, Current)
FolderList = [i if 'Grid' in i else '' for i in FolderList]
ERIFolders = [i if 'ERI' in i else '' for i in FolderList]
HamamatsuFolders = [i if 'Hamamatsu' in i else '' for i in FolderList]
# Disregard now emtpy list elements: http://stackoverflow.com/a/3845449
ERIFolders = [x for x in ERIFolders if x]
HamamatsuFolders = [x for x in HamamatsuFolders if x]

ChosenERI = ask_user('Which ERI folder shall we use?', ERIFolders)
ChosenHamamatsu = ask_user('Which Hamamatsu folder shall we use to compare with %s?' % bold(ChosenERI), HamamatsuFolders)

# Prepare output directory
OutputPath = os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                          'ERI-Analysis', 'Images', 'Brightness-Comparison')
try:
    os.makedirs(OutputPath)
except OSError:
    # Directory already exists
    pass

# Grab Voltage and Current for ERI
ImageListERI = sorted(glob.glob(os.path.join(StartPath, ChosenERI, '*.raw')))
print 'Reading Parameters from %s images in %s' % (len(ImageListERI),
                                                   bold(ChosenERI))
VoltageERI = [int(os.path.basename(i).split('_')[1][:-2]) for i in ImageListERI]
CurrentERI = [int(os.path.basename(i).split('_')[2][:-2]) for i in ImageListERI]

# Grab Voltage and Current for Hamamatsu
ImageListHamamatsu = sorted(glob.glob(os.path.join(StartPath, ChosenHamamatsu,
                                                   '*.raw')))

print 'Reading Parameters from %s images in %s' % (len(ImageListERI),
                                                   bold(ChosenHamamatsu))
VoltageHamamatsu = [int(os.path.basename(i).split('_')[1][:-2]) for i in
                    ImageListHamamatsu]
CurrentHamamatsu = [int(os.path.basename(i).split('_')[2][:-2]) for i in
                    ImageListHamamatsu]

# Grab closest values from the Hamamatsu dataset and plot them afterwards
plt.ion()
plt.figure(figsize=[8, 6])
CompareImages = []
for c, i in enumerate(ImageListERI):
    print 80 * '-'
    print 'Finding best matching current from Hamamatsu for %s (%s kV, ' \
          '%s mA)' % (os.path.basename(i), VoltageERI[c], CurrentERI[c])
    Candidates = []
    for k in ImageListHamamatsu:
        if str(VoltageERI[c]) + 'kV' in k:
            Candidates.append(k)
    IndexList = [ImageListHamamatsu.index(i) for i in Candidates]
    # Get the closest value to the current from Hamamatsu list. Based on
    # http://stackoverflow.com/a/9706105/323100
    ChosenOne = min(enumerate([CurrentHamamatsu[i] for i in IndexList]),
                    key=lambda x: abs(x[1] - CurrentERI[c]))
    print 'Found a match in %s' % os.path.basename(Candidates[ChosenOne[0]])
    CompareImages.append(Candidates[ChosenOne[0]])
print 80 * '-'

VoltageMatch = [int(os.path.basename(i).split('_')[1][:-2]) for i in
                CompareImages]
CurrentMatch = [int(os.path.basename(i).split('_')[2][:-2]) for i in
                CompareImages]

plt.scatter(VoltageHamamatsu, CurrentHamamatsu, c=colors[0], alpha=0.25,
            label='Hamamatsu')
plt.plot(VoltageERI, CurrentERI, c=colors[1], label='ERI')
plt.plot(VoltageMatch, CurrentMatch, c=colors[2], label='Best Match')
plt.legend(loc='upper left')
plt.xlabel('Voltage [kV]')
plt.ylabel('Current [uA]')
plt.xlim([20, 70])
plt.ylim([0, 60])
plt.draw()
plt.savefig(os.path.join(OutputPath, 'Match-' +
                         os.path.basename(os.path.dirname(CompareImages[0])) +
                         '_vs_' +
                         os.path.basename(os.path.dirname(ImageListERI[0])) +
                         '.png'))

# Plot brightness of the comparable images in one plot
BrightnessHamamatsu = []
BrightnessERI = []
DisplayProgress = True
plt.figure(figsize=[20, 9])
for c, i in enumerate(CompareImages):
    print '%s/%s: Comparing %s with %s' % (c + 1, len(CompareImages),
                                           os.path.basename(i),
                                           os.path.basename(
                                               ImageListERI[c]))
    ImageERI = read_raw(ImageListERI[c])
    ImageHamamatsu = read_raw(i)
    BrightnessERI.append(numpy.mean(ImageERI))
    BrightnessHamamatsu.append(numpy.mean(ImageHamamatsu))

# Scale with transmission, according to http://web-docs.gsi.de/~stoe_exp/web_programs/x_ray_absorption/index.php
Beryllium = numpy.linspace(0.9945, 0.9959, len(BrightnessHamamatsu))
SiO2 = numpy.linspace(0.7370, 0.9538, len(BrightnessERI))
BrightnessERI = BrightnessERI / SiO2
BrightnessHamamatsu = BrightnessHamamatsu / Beryllium

BrightnessRatio = [a / b for a, b in zip(BrightnessHamamatsu, BrightnessERI)]

# Plot Brightness with kV as x-axis (Image 0 is 25 kV)
plt.subplot(231)
# First plot maximal and median images
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         BrightnessERI[BrightnessRatio.index(numpy.median(BrightnessRatio))],
         color=colors[0], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         BrightnessHamamatsu[BrightnessRatio.index(numpy.median(
             BrightnessRatio))],
         color=colors[1], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)),
         BrightnessERI[BrightnessRatio.index(max(BrightnessRatio))],
         color=colors[2], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)),
         BrightnessHamamatsu[BrightnessRatio.index(max(BrightnessRatio))],
         color=colors[3], marker='o', markersize=15)
# Plot all values
plt.plot(range(25, 25 + len(BrightnessERI)), BrightnessERI, c=colors[0],
         label=os.path.basename(os.path.dirname(ImageListERI[0])))
plt.plot(range(25, 25 + len(BrightnessHamamatsu)), BrightnessHamamatsu,
         c=colors[1], label=os.path.basename(os.path.dirname(i)))
plt.xlim([20, 70])
plt.ylim([0, 2 ** 12])
plt.xlabel('kV')
plt.ylabel('Mean image brightness')
plt.title('Average brightness to voltage')
plt.legend(loc='best')

# Plot Ratio with kV as x-axis (Image 0 is 25 kV)
plt.subplot(234)
plt.plot(range(25, 25 + len(BrightnessERI)), BrightnessRatio, 'k',
         label='Hamamatsu / ERI')
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)), max(BrightnessRatio),
         color='red', marker='o', markersize=15, alpha=0.309,
         label='Maximal difference (%0.2fx)' % max(BrightnessRatio))
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         numpy.median(BrightnessRatio), color='green', marker='o',
         markersize=15, alpha=0.309,
         label='Median difference (%0.2fx)' % numpy.median(BrightnessRatio))
plt.xlim([20, 70])
plt.ylim([0, 6])
plt.legend(loc='best')
plt.xlabel('kV')
plt.ylabel('Relative brightness')
plt.title('Brightness difference')
# Show images from max and median
plt.subplot(232)
plt.title('Median difference image Hamamatsu\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(CompareImages[BrightnessRatio.index(numpy.median(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[1],
                                alpha=0.309))
plt.axis('off')
plt.subplot(235)
plt.title('Median difference image ERI\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(ImageListERI[BrightnessRatio.index(
    numpy.median(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[0],
                                alpha=0.309))
plt.axis('off')
plt.subplot(233)
plt.title('Maximal difference image Hamamatsu\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(CompareImages[BrightnessRatio.index(max(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[3], alpha=0.309))
plt.axis('off')
plt.subplot(236)
plt.title('Maximal difference image ERI\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(ImageListERI[BrightnessRatio.index(max(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[2], alpha=0.309))
plt.axis('off')
plt.draw()
plt.savefig(os.path.join(OutputPath, 'Comparison-' +
                         os.path.basename(os.path.dirname(CompareImages[0])) +
                         '_vs_' +
                         os.path.basename(os.path.dirname(ImageListERI[0])) +
                         '.png'))
plt.ioff()
plt.show()
print 'Done with everything!'
