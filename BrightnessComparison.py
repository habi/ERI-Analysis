# -*- coding: utf-8 -*-

"""
BrightnessComparison | David Haberthür <david.haberthuer@psi.ch>

Script to get compare the brightness of the images from ERI and
Hamamatsu
"""

# Imports
import numpy
import os
import glob
import matplotlib.pylab as plt


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

ChosenERI = AskUser('Which ERI folder shall we use?', ERIFolders)
ChosenHamamatsu = AskUser('Which Hamamatsu folder shall we use to compare '
                          'with %s?' % bold(ChosenERI), HamamatsuFolders)

# Prepare output directory
OutputPath = os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                          'ERI-Analysis', 'Images', 'Brightness-' +
                          os.path.basename(ChosenERI) + '_VS_' +
                          os.path.basename(ChosenHamamatsu))
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
plt.figure(figsize=[16, 9])
CompareImages = []
for c, i in enumerate(ImageListERI):
    print 80 * '-'
    print 'Finding best matching current from Hamamatsu for %s (%s kV, ' \
          '%s mA)' % (i, VoltageERI[c], CurrentERI[c])
    Candidates = []
    for k in ImageListHamamatsu:
        if str(VoltageERI[c]) + 'kV' in k:
            Candidates.append(k)
    IndexList = [ImageListHamamatsu.index(i) for i in Candidates]
    # Get the closest value to the current from Hamamatsu list. Based on
    # http://stackoverflow.com/a/9706105/323100
    ChosenOne = min(enumerate([CurrentHamamatsu[i] for i in IndexList]),
                    key=lambda x: abs(x[1]-CurrentERI[c]))
    print 'Found a match in %s' % Candidates[ChosenOne[0]]
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
plt.legend(loc='best')
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
plt.figure(figsize=[16, 9])
for c, i in enumerate(CompareImages):
    print '%s/%s: Comparing %s with %s' % (c + 1, len(CompareImages),
                                           os.path.basename(i),
                                           os.path.basename(
                                               ImageListERI[c]))
    ImageERI = read_raw(ImageListERI[c])
    ImageHamamatsu = read_raw(i)
    BrightnessERI.append(numpy.mean(ImageERI))
    BrightnessHamamatsu.append(numpy.mean(ImageHamamatsu))
# Plot Brightness with kV as x-axis (Image 0 is 25 kV)
plt.subplot(211)
plt.plot(range(25, 25 + len(BrightnessHamamatsu)), BrightnessHamamatsu,
         c=colors[2], label=os.path.basename(os.path.dirname(i)))
plt.plot(range(25, 25 + len(BrightnessERI)), BrightnessERI, c=colors[1],
         label=os.path.basename(os.path.dirname(ImageListERI[0])))
plt.xlim([20, 70])
plt.ylim([0, 2**12])
plt.xlabel('kV')
plt.ylabel('Mean image brightness')
plt.title('Average brightness compared to current')
plt.legend(loc='best')

plt.subplot(212)
plt.plot([a/b for a, b in zip(BrightnessHamamatsu, BrightnessERI)],
         label='Hamamatsu / ERI')
plt.ylim([0, 6])
plt.legend(loc='best')
plt.title('Brightness difference')
# plt.tight_layout()
plt.draw()
plt.savefig(os.path.join(OutputPath, 'Brightness-' +
                         os.path.basename(os.path.dirname(CompareImages[0])) +
                         '_vs_' +
                         os.path.basename(os.path.dirname(ImageListERI[0])) +
                         '.png'))
plt.ioff()
plt.show()
print 'Done with everything!'

