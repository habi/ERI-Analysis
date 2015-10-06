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

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ImageFolders = sorted(glob.glob(os.path.join(StartPath, '*')))
for c, i in enumerate(ImageFolders):
    print '%s: %s' % (c, os.path.basename(i))

Flat = glob.glob(os.path.join(ImageFolders[1], '*40kV*.raw'))[0]
Image = glob.glob(os.path.join(ImageFolders[2], '*40kV*.raw'))[0]

FlatImage = read_raw(Flat)
ImageImage = read_raw(Image)
CorrectedImage = ImageImage - FlatImage

plt.subplot(311)
plt.imshow(FlatImage)
plt.title('flat')
plt.subplot(312)
plt.imshow(ImageImage)
plt.title('image')
plt.subplot(313)
plt.imshow(CorrectedImage)
plt.title('corrected image')
plt.show()
