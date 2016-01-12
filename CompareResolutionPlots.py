# -*- coding: utf-8 -*-

"""
CompareResolutionsPlots.py | David Haberthür <david.haberthuer@psi.ch>

Script to compare two line profile plots with eatch other.
"""

# Imports
import os
import glob
import numpy
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
import matplotlib.gridspec as gridspec


def AskUser(Blurb, Choices):
    """
    Ask for user input.
    Based on function in MasterThesisIvan.ini
    """
    print(Blurb)
    for Counter, Item in enumerate(sorted(Choices)):
        print '    * [' + str(Counter) + ']:', Item
    Selection = []
    while Selection not in range(len(Choices)):
        try:
            Selection = int(input(' '.join(['Please enter the choice you',
                                            'want [0-' +
                                            str(len(Choices) - 1) +
                                            ']:'])))
        except:
            print 'You actually have to select *something*'
        if Selection not in range(len(Choices)):
            print 'Try again with a valid choice'
    print 'You selected', sorted(Choices)[Selection]
    return sorted(Choices)[Selection]


def bold(msg):
    """
    Enable bold and colorful output on the command line (http://is.gd/HCaDv9)
    """
    return u'\033[1m%s\033[0m' % msg


# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=2, marker='o')
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
colors = ["#84DEBD", "#D1B9D4", "#D1D171"]

StartPath = '/sls/X02DA/data/e13960/Data20/CNT/ERI-Analysis/Images/'
# Filter list for only 'Grid' folders: http://stackoverflow.com/a/4260304
FolderList = [i if 'Grid' in i else '' for i in
              sorted(os.walk(StartPath).next()[1])]
# Filter list to remove OutputFolders
FolderList = [i if 'Comparison' not in i else '' for i in FolderList]
ERIFolders = [i if 'ERI' in i else '' for i in FolderList]
HamamatsuFolders = [i if 'Hamamatsu' in i else '' for i in FolderList]
# Disregard now emtpy list elements: http://stackoverflow.com/a/3845449
ERIFolders = [x for x in ERIFolders if x]
HamamatsuFolders = [x for x in HamamatsuFolders if x]

ChosenERI = AskUser('Which ERI folder shall we use?', ERIFolders)
ChosenHamamatsu = AskUser('Which Hamamatsu folder shall we use to compare '
                          'with %s?' % bold(ChosenERI), HamamatsuFolders)


# Prepare output directory
OutputPath = os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                          'ERI-Analysis', 'Images', 'Resolution-Comparison',
                          'Comparison-' +
                          os.path.basename(ChosenERI) + '_VS_' +
                          os.path.basename(ChosenHamamatsu))
try:
    os.makedirs(OutputPath)
except OSError:
    # Directory already exists
    pass

ImageListERI = sorted(glob.glob(os.path.join(StartPath, ChosenERI, '*.png')))
print 'Reading Parameters from %s images in %s' % (len(ImageListERI),
                                                   bold(ChosenERI))
VoltageERI = [int(os.path.basename(i).split('_')[1][:-2]) for i in ImageListERI]
CurrentERI = [int(os.path.basename(i).split('_')[2][:-2]) for i in ImageListERI]

ImageListHamamatsu = sorted(glob.glob(os.path.join(StartPath, ChosenHamamatsu,
                                                   '*.png')))
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

# Display results
plt.ion()
plt.figure(figsize=[18, 12])
gs = gridspec.GridSpec(4, 4)
plt.subplot(gs[1:3, 0])
plt.scatter(VoltageHamamatsu, CurrentHamamatsu, c=colors[0], alpha=0.25,
            label='Hamamatsu')
plt.plot(VoltageERI, CurrentERI, c=colors[1], label='ERI')
plt.plot(VoltageMatch, CurrentMatch, c=colors[2], label='Closest Match')
plt.xlabel('Voltage [kV]')
plt.ylabel('Current [uA]')
plt.ylim([0, 75])
plt.legend(loc='best')
plt.title('Voltage vs. Current')
for c, i in enumerate(CompareImages):
    print '%s/%s | %s kV/%s uA | Comparing %s with %s' % (
        c + 1, len(CompareImages), VoltageERI[c], CurrentERI[c],
        bold(os.path.basename(i)),
        bold(os.path.basename(ImageListERI[c])))
    ImageERI = plt.imread(ImageListERI[c])
    ImageHamamatsu = plt.imread(i)
    plt.subplot(gs[:2, 1:])
    plt.imshow(plt.imread(ImageListERI[c]))
    plt.axis('off')
    plt.subplot(gs[2:, 1:])
    plt.imshow(plt.imread(i))
    plt.axis('off')
    plt.subplots_adjust(wspace=0.02, hspace=0, left=0.03, right=1,
                        top=1, bottom=0)
    plt.draw()
    # Save figure and concatenated results
    plt.savefig(os.path.join(OutputPath, '%02d' % VoltageERI[c] + 'kV' +
                             str(CurrentERI[c]) + 'uA.png'))
    ConcatenateImage = numpy.concatenate((ImageERI, ImageHamamatsu), axis=0)
    plt.imsave(os.path.join(OutputPath, 'Concatenate_%02d' % VoltageERI[c] +
                            'kV' + str(CurrentERI[c]) + 'uA.png'),
               ConcatenateImage)

plt.ioff()
plt.show()
print 'Done with everything!'

