# -*- coding: utf-8 -*-

"""
ImageBrightness | David Haberthür <david.haberthuer@psi.ch>

Script to get insight into the brightness of the images shot with the the
ShadoBox.
Adapted from DarkImages.py
"""

# Imports
import platform
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


def ask_user(blurb, choices):
    """
    Ask for user input.
    Based on function in MasterThesisIvan.ini
    """
    print(blurb)
    for Counter, Item in enumerate(sorted(choices)):
        print '    * [' + str(Counter) + ']:', Item
    selection = []
    while selection not in range(len(choices)):
        try:
            selection = int(input(' '.join(['Please enter the choice you',
                                            'want [0-' +
                                            str(len(choices) - 1) +
                                            ']:'])))
        except:
            print 'You actually have to select *something*'
        if selection not in range(len(choices)):
            print 'Try again with a valid choice'
    print 'You selected', sorted(choices)[selection]
    return sorted(choices)[selection]

# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=2)
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
colors = ["#84DEBD", "#D1B9D4", "#D1D171"]

# Reading images
if 'anomalocaris' in platform.node() or 'vpn' in platform.node():
    print 'Running on OSX, setting different start path'
    StartPath = os.path.join('/Volumes', 'e13960', 'Data20', 'Gantry',
                             'Images')
else:
    StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry',
                             'Images')
# Exclude 'Darks' folder with *-*
Folders = glob.glob(os.path.join(StartPath, '*-*'))
Folders = [os.path.basename(f) for f in Folders]
SelectedFolder = ask_user('Which folder do you want to look at?', Folders)
ImageNames = sorted(glob.glob(os.path.join(StartPath, SelectedFolder,
                                           '*.raw')))
if not ImageNames:
    exit('No images found, is "%s" the correct directory?' % StartPath)
print 'Reading in %s images in %s' % (len(ImageNames),
                                      os.path.basename(SelectedFolder))
Images = [read_raw(i) for i in ImageNames]

# Calculating values
print 'Calculating average image'
MeanImage = numpy.mean(Images, axis=0)
print 'Extracting mean (brightness) of %s raw images' % len(ImageNames)
Brightness = [numpy.mean(i) for i in Images]
print 'Extracting gray value STD of %s raw images' % len(ImageNames)
STD = [numpy.std(i) for i in Images]

plt.figure(figsize=[16, 9])
plt.subplot(221)
plt.imshow(MeanImage)
plt.title('Average image with a min of %s and a max of'
          ' %s' % (numpy.min(MeanImage), numpy.max(MeanImage)))
plt.subplot(222)
std = 3
plt.imshow(contrast_stretch(MeanImage, std=std))
plt.title('Contrast stretched average image (mean +- %s STD)' % std)
plt.subplot(223)
plt.plot(Brightness, c=colors[0], label='Image mean (%0.2f-%0.2f)' % (
    numpy.min(Brightness), numpy.max(Brightness)))
plt.axhline(numpy.mean(MeanImage), c=colors[1], alpha=0.5,
            label='Mean of average image: %0.2f' % numpy.mean(MeanImage))
plt.axhline(numpy.mean(Brightness), c=colors[2], alpha=0.5,
            label='Mean of Brightness: %0.2f' % numpy.mean(Brightness))
plt.legend(loc='best')
plt.title('Brightness of %s images' % len(Images))
plt.subplot(224)
plt.plot(STD, c=colors[0], label='STD (%0.2f-%0.2f)' % (numpy.min(STD),
                                                        numpy.max(STD)))
plt.axhline(numpy.std(MeanImage), c=colors[1],
            label='STD of average image: %0.2f' % numpy.std(MeanImage))
plt.axhline(numpy.mean(STD), c=colors[2],
            label='Mean of STD: %0.2f' % numpy.mean(STD))
plt.legend(loc='best')
plt.title('STD of %s images' % len(Images))

if 'anomalocaris' in platform.node() or 'vpn' in platform.node():
    print 'Running on OSX, setting different start path'
    SaveBase = os.path.join('/Volumes', 'e13960')
else:
    SaveBase = os.path.expanduser('~')
plt.savefig(os.path.join(SaveBase, 'Data20', 'CNT',
                         'ERI-Analysis', 'Images',
                         'Brightness-' + SelectedFolder + '.png'))

plt.show()
