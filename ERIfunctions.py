"""
Functions that we use over and over for analyzing the ERI data.
And some consistent settings for display.
"""

# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=2, marker='o')
# Show background grid
plt.rc('axes', grid=True)

import numpy

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


def ask_user(Blurb, Choices):
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
