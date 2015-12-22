"""
FlatCorrection.py | David Haberthuer
<david.haberthuer@psi.ch>

Script to correct the images with the flats.
"""

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
    image = numpy.fromfile(filename, dtype=numpy.uint16,
                           count=-1).reshape(height, width).byteswap()
    # Flip image upside down and left-right, so we can look at it without
    # craning our neck.
    image = numpy.flipud(image)

    return image


def ask_user(blurb, choices):
    """
    Ask for user input.
    Based on function in MasterThesisIvan.ini
    """
    print(blurb)
    for Counter, Item in enumerate(sorted(choices)):
        print '\t* [' + str(Counter) + ']:', Item
    selection = []
    while selection not in range(len(choices)):
        try:
            selection = int(input(' '.join(['Please enter the choice you want',
                                            '[0-' + str(len(choices) - 1) +
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

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ImageFolders = sorted(glob.glob(os.path.join(StartPath, '*')))
for c, folder in enumerate(ImageFolders):
    print 'Folder %s (%s) contains %s files' % (c, os.path.basename(folder),
                                                len(glob.glob(os.path.join(
                                                    folder, '*.raw'))))

print 80 * '-'

FlatFolder = ask_user('From which folder should we load the flats?',
                      ImageFolders[1:])
ProjectionFolder = ask_user('From which folder should we load the images '
                            'from?', ImageFolders[1:])

LoadEvery = 1
# Load dark images
print 'Loading every %sth dark image' % LoadEvery
DarkNames = sorted(glob.glob(os.path.join(StartPath, 'Darks',
                                          '*.raw')))[::LoadEvery]
print '\tReading in %s images in %s' % (len(DarkNames),
                                        os.path.join(StartPath, 'Darks'))
DarkImages = [read_raw(i) for i in DarkNames]
print 'Calculating average of %s dark images' % len(DarkImages)
AverageDark = numpy.average(DarkImages, axis=0)

# Loading flat images
print 'Loading every %sth flat image' % LoadEvery
FlatNames = sorted(glob.glob(os.path.join(FlatFolder, '*.raw')))[::LoadEvery]
print '\tReading in %s images in %s' % (len(FlatNames), FlatFolder)
FlatImages = [read_raw(i) for i in FlatNames]
# Calculating values
print 'Calculating average of %s flat images' % len(FlatImages)
AverageFlat = numpy.average(FlatImages, axis=0)

plt.ion()
plt.figure(figsize=[16, 10])

# Loading projections and correcting each one
ProjectionImages = sorted(glob.glob(os.path.join(ProjectionFolder, '*.raw')))
for c, p in enumerate(ProjectionImages):
    print '%s/%s: Reading projection %s' % (c + 1, len(ProjectionImages),
                                            os.path.basename(p))
    ProjectionImage = read_raw(p)
    Voltage = int(p.split('_')[1][:-2])
    Current = int(p.split('_')[2][:-2])
    ExposureTime = int(p.split('_')[3][:-4])

    # P=-ln((P-D)/(F-D)), while D and F are mean darks and mean flats
    CorrectedImage = numpy.negative(numpy.log(numpy.divide(
        numpy.subtract(ProjectionImage, AverageDark),
        numpy.subtract(AverageFlat, AverageDark))))

    plt.clf()
    plt.subplot(231)
    plt.imshow(AverageFlat)
    plt.title('Average flat')
    plt.subplot(232)
    plt.imshow(AverageDark)
    plt.title('Average dark')
    plt.subplot(233)
    plt.imshow(ProjectionImage)
    plt.title('Raw projection\n(%s)' % os.path.basename(p))
    plt.subplot(212)
    plt.imshow(CorrectedImage)
    plt.title('Corrected image')
    plt.suptitle('%s\nImage acquired at %skV and %suA\nwith a Detector '
                 'exposure time of %ss' % (os.path.basename(p.split('_')[0]),
                                           Voltage, Current, ExposureTime))
    plt.savefig(os.path.splitext(p)[0] + '.figure.png')
    plt.imsave(os.path.splitext(p)[0] + '.corrected.png', CorrectedImage)
    plt.draw()

print 'Done'
plt.ioff()
plt.show()
