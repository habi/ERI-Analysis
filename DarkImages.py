# -*- coding: utf-8 -*-

"""
DarkImages | David Haberthür <david.haberthuer@psi.ch>

Script to get insight into the dark images from the ShadoBox
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

# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=2)
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
colors = ["#84DEBD", "#D1B9D4", "#D1D171"]

# Reading images
StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images',
                         'Darks')
DarkNames = glob.glob(os.path.join(StartPath, '*.raw'))
print 'Reading in %s images in %s' % (len(DarkNames), StartPath)
DarkImages = [read_raw(i) for i in DarkNames]
# Calculating values
print 'Calculating average dark image'
MeanImage = numpy.average(DarkImages, axis=0)
print 'Extracting brightness brightness of %s raw images' % len(DarkNames)
Brightness = [numpy.mean(i) for i in DarkImages]
print 'Extracting gray value STD of %s raw images' % len(DarkNames)
STD = [numpy.std(i) for i in DarkImages]

plt.figure(figsize=[16, 9])
plt.subplot(211)
plt.imshow(MeanImage)
plt.title('Mean dark image')
plt.subplot(223)
plt.plot(Brightness, c=colors[0], label='Image mean')
plt.axhline(numpy.mean(MeanImage), c=colors[1], label='Mean of average image')
plt.axhline(numpy.mean(Brightness), c=colors[2], label='Mean of Brightness')
plt.legend(loc='best')
plt.title('Brightness of %s images' % len(DarkImages))
plt.subplot(224)
plt.plot(STD, c=colors[0], label='STD')
plt.axhline(numpy.std(MeanImage), c=colors[1], label='STD of average image')
plt.axhline(numpy.mean(STD), c=colors[2], label='Mean of STD')
plt.legend(loc='best')
plt.title('STD of %s images' % len(DarkImages))
plt.show()
