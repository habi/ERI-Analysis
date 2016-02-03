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
from scipy import stats

from ERIfunctions import *

# Reset markers from standard
#~ plt.rc('lines', linewidth=2, marker='o')
# Colors from 'I want hue'
colors = ["#B459CA",
	  "#5E913F",
	  "#C06130",
	  "#C84C78",
	  "#6A7AB2"]

Ubuntu = False
if Ubuntu:
    StartPath = '/afs/psi.ch/user/h/haberthuer/slsbl/x02da/e13960/Data20/Gantry/Images'
else:
    StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'

# Filter list for only 'Grid' folders: http://stackoverflow.com/a/4260304
FolderList = sorted(os.walk(StartPath).next()[1])
# Filter list to remove the folders to disregard
FolderList = [i if 'DoNotUse' not in i else '' for i in FolderList]
# Only show these folders (Wrench, Grid, Current)
FolderList = [i if 'Wrench' in i else '' for i in FolderList]
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

print 'Reading Parameters from %s images in %s' % (len(ImageListHamamatsu),
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
    print 'Looking for best matching current from Hamamatsu for %s (%s kV, %s mA)' % (os.path.basename(i), VoltageERI[c], CurrentERI[c])
    Candidates = []
    for k in ImageListHamamatsu:
        if str(VoltageERI[c]) + 'kV' in k:
            Candidates.append(k)
    IndexList = [ImageListHamamatsu.index(i) for i in Candidates]
    # Get the closest value to the current from Hamamatsu list. Based on
    # http://stackoverflow.com/a/9706105/323100
    ChosenOne = min(enumerate([CurrentHamamatsu[i] for i in IndexList]),
                    key=lambda x: abs(x[1] - CurrentERI[c]))
    print '\tFound a match in %s' % os.path.basename(Candidates[ChosenOne[0]])
    CompareImages.append(Candidates[ChosenOne[0]])

VoltageMatch = [int(os.path.basename(i).split('_')[1][:-2]) for i in
                CompareImages]
CurrentMatch = [int(os.path.basename(i).split('_')[2][:-2]) for i in
                CompareImages]

plt.scatter(VoltageHamamatsu, CurrentHamamatsu, c=colors[0], alpha=0.309,
            label='Hamamatsu')
plt.plot(VoltageERI, CurrentERI, c=colors[1], label='ERI', marker='o')
plt.plot(VoltageMatch, CurrentMatch, c=colors[2], label='Best Match', marker='o')
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
STDERI = []
STDHamamatsu = []
DisplayProgress = True
plt.figure(figsize=[20, 9])
for c, i in enumerate(CompareImages):
    print '%s/%s: Comparing %s with %s' % (c + 1, len(CompareImages),
                                           os.path.basename(ImageListERI[c]),
                                           os.path.basename(i))
    ImageERI = read_raw(ImageListERI[c])
    ImageHamamatsu = read_raw(i)
    BrightnessERI.append(numpy.mean(ImageERI))
    STDERI.append(numpy.std(ImageERI, axis=None, ddof=0))
    BrightnessHamamatsu.append(numpy.mean(ImageHamamatsu))
    STDHamamatsu.append(numpy.std(ImageHamamatsu, axis=None, ddof=0))

# Scale with transmission, according to http://web-docs.gsi.de/~stoe_exp/web_programs/x_ray_absorption/index.php
Scale = True
if Scale:
    Beryllium = numpy.linspace(0.9945, 0.9959, len(BrightnessHamamatsu))
    SiO2 = numpy.linspace(0.7370, 0.9538, len(BrightnessERI))
    BrightnessERI = BrightnessERI / SiO2
    BrightnessHamamatsu = BrightnessHamamatsu / Beryllium
    STDERI = STDERI / SiO2
    STDHamamatsu = STDHamamatsu / Beryllium
else:
    BrightnessERI = numpy.array(BrightnessERI)
    BrightnessHamamatsu = numpy.array(BrightnessHamamatsu)
    STDERI = numpy.array(STDERI)
    STDHamamatsu = numpy.array(STDHamamatsu)


BrightnessRatio = [a / b for a, b in zip(BrightnessHamamatsu, BrightnessERI)]

# Plot Brightness with kV as x-axis (Image 0 is 25 kV)
plt.subplot(241)
# First plot brightness values ± STD
currentplot = plt.gca()
currentplot.fill_between(range(25, 25 + len(BrightnessERI)), BrightnessERI + STDERI, BrightnessERI - STDERI, facecolor=colors[0], edgecolor='w', alpha=0.309)
currentplot.fill_between(range(25, 25 + len(BrightnessHamamatsu)), BrightnessHamamatsu + STDHamamatsu, BrightnessHamamatsu - STDHamamatsu, facecolor=colors[1], edgecolor='w', alpha=0.309)
# Then plot a marker for the minimal, maximal and median images
plt.plot(25 + BrightnessRatio.index(min(BrightnessRatio)),
         BrightnessERI[BrightnessRatio.index(min(BrightnessRatio))],
         color=colors[2], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(min(BrightnessRatio)),
         BrightnessHamamatsu[BrightnessRatio.index(min(BrightnessRatio))],
         color=colors[2], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         BrightnessERI[BrightnessRatio.index(numpy.median(BrightnessRatio))],
         color=colors[3], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         BrightnessHamamatsu[BrightnessRatio.index(numpy.median(BrightnessRatio))],
         color=colors[3], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)),
         BrightnessERI[BrightnessRatio.index(max(BrightnessRatio))],
         color=colors[4], marker='o', markersize=15)
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)),
         BrightnessHamamatsu[BrightnessRatio.index(max(BrightnessRatio))],
         color=colors[4], marker='o', markersize=15)
# Finally plot the brightness values on top of that
plt.plot(range(25, 25 + len(BrightnessERI)), BrightnessERI, c=colors[0],
         label=r'%s $\pm$ STD' % os.path.basename(os.path.dirname(ImageListERI[0])))
plt.plot(range(25, 25 + len(BrightnessHamamatsu)), BrightnessHamamatsu,
         c=colors[1], label=r'%s $\pm$ STD' % os.path.basename(os.path.dirname(ImageListHamamatsu[0])))
plt.xlim([20, 70])
plt.ylim([0, 2 ** 12])
plt.xlabel('kV')
plt.ylabel('Gray value')
if Scale:
    plt.title('Mean brightness to voltage\n(Adjusted for transmission of output window)')
else:
    plt.title('Mean brightness to voltage')
plt.legend(loc='best')

# Plot Ratio with kV as x-axis (Image 0 is 25 kV)
plt.subplot(245)
plt.plot(range(25, 25 + len(BrightnessERI)), BrightnessRatio, 'k',
         label='Hamamatsu / ERI')
plt.plot(25 + BrightnessRatio.index(min(BrightnessRatio)), min(BrightnessRatio),
         color=colors[2], marker='o', markersize=15, alpha=0.309,
         label='Minimal difference (%0.2fx)' % min(BrightnessRatio))
plt.plot(25 + BrightnessRatio.index(numpy.median(BrightnessRatio)),
         numpy.median(BrightnessRatio), color=colors[3], marker='o', markersize=15,
         alpha=0.309, label='Median difference (%0.2fx)' % numpy.median(BrightnessRatio))
plt.plot(25 + BrightnessRatio.index(max(BrightnessRatio)), max(BrightnessRatio),
         color=colors[4], marker='o', markersize=15, alpha=0.309,
         label='Maximal difference (%0.2fx)' % max(BrightnessRatio))
plt.xlim([20, 70])
plt.ylim([0, 6])
plt.legend(loc='best')
plt.xlabel('kV')
plt.ylabel('Relative brightness')
plt.title('Brightness difference')
# Show images from min, max and median
plt.subplot(242)
plt.title('Minimal difference image Hamamatsu\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(CompareImages[BrightnessRatio.index(min(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[2], alpha=0.309))
plt.axis('off')
plt.subplot(246)
plt.title('Minimal difference image ERI\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(ImageListERI[BrightnessRatio.index(min(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[2], alpha=0.309))
plt.axis('off')
plt.subplot(243)
plt.title('Median difference image Hamamatsu\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(CompareImages[BrightnessRatio.index(numpy.median(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[3], alpha=0.309))
plt.axis('off')
plt.subplot(247)
plt.title('Median difference image ERI\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(ImageListERI[BrightnessRatio.index(
    numpy.median(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[3], alpha=0.309))
plt.axis('off')
plt.subplot(244)
plt.title('Maximal difference image Hamamatsu\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(CompareImages[BrightnessRatio.index(max(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[4], alpha=0.309))
plt.axis('off')
plt.subplot(248)
plt.title('Maximal difference image ERI\n(contrast stretched)')
plt.imshow(contrast_stretch(read_raw(ImageListERI[BrightnessRatio.index(max(BrightnessRatio))])))
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((0, 0), 2048, 1024, color=colors[4], alpha=0.309))
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
