# -*- coding: utf-8 -*-

"""
ResolutionPlotter.py | David Haberthür <david.haberthuer@psi.ch>

Script to plot a line through some of the regions of the resolution phantom.
"""

# Imports
import numpy
import os
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
from matplotlib.patches import Rectangle

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

def gaussianfit(data):
    from scipy.optimize import curve_fit
    # Define gaussian model function which we use to calculate a fit to the data
    def gauss(x, *p):
        A, mu, sigma = p
        return A * numpy.exp(-(x - mu)**2 / (2. * sigma**2))
    # Fit with initial guess p0
    p0 = [1, 0, 0.2]
    coeff, var_matrix = curve_fit(gauss, range(0, len(data)), data, p0=p0)
    return gauss(range(0,len(data)), *coeff)

def LSF(edgespreadfunction):
    return numpy.diff(edgespreadfunction)

def MTF(linespreadfunction):
    return numpy.abs(numpy.fft.fft(linespreadfunction))[:len(
        linespreadfunction) / 2]

def normalize(data):
    return (data - numpy.min(data)) / (numpy.max(data) - numpy.min(data))

# Display all images consistently
plt.rc('image', cmap='gray', interpolation='nearest')
# Make lines a bit wider
plt.rc('lines', linewidth=3)
# Show background grid
plt.rc('axes', grid=True)
# Colors from 'I want hue'
Colors = ["#E9AE70",
"#7DDCD8",
"#E7B0CF",
"#9DE380",
"#6CE3AF",
"#ABC7E5",
"#D8D867",
"#B5D79B"]

# Load images
StartPath = '/sls/X02DA/data/e13960/Data20/Gantry/Images'
ERIName = os.path.join(StartPath, 'ERI-Grid4-15s-Exposure',
                       'ERI_060kV_029uA_15sExp_01.raw')
HamamatsuName = os.path.join(StartPath, 'Hamamatsu-Grid4-15s-Exposure',
                             'Hamamatsu_060kV_030uA_15sExp_01.raw')
ERIImage = read_raw(ERIName)
HamamatsuImage = read_raw(HamamatsuName)

# Crop to interesting region (slanted edge of resolution phantom)
CropRegion = [100, 900, 550, 700]  # left
CropRegion = [100, 900, 1600, 1750]  # right
ERICrop = ERIImage[CropRegion[0]:CropRegion[1], CropRegion[2]:CropRegion[3]]
HamamatsuCrop = HamamatsuImage[CropRegion[0]:CropRegion[1],
                               CropRegion[2]:CropRegion[3]]

# Calculate average Edge response
ERIResponse = numpy.mean(ERICrop, axis=0)
HamamatsuResponse = numpy.mean(HamamatsuCrop, axis=0)

# Display images with region of crop
plt.figure(figsize=[20, 9])
plt.subplot(251)
plt.title(os.path.basename(ERIName))
plt.imshow(ERIImage)
# Draw crop region in original image
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((CropRegion[2], CropRegion[0]),
                                CropRegion[3] - CropRegion[2],
                                CropRegion[1] - CropRegion[0], facecolor='red',
                                edgecolor='w', alpha=0.125))
plt.subplot(256)
plt.title(os.path.basename(HamamatsuName))
plt.imshow(HamamatsuImage)
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((CropRegion[2], CropRegion[0]),
                                CropRegion[3] - CropRegion[2],
                                CropRegion[1] - CropRegion[0], facecolor='red',
                                edgecolor='w', alpha=0.125))
# Display cropped region
plt.subplot(252)
plt.title('ERI')
plt.imshow(ERICrop)
plt.subplot(257)
plt.title('Hamamatsu')
plt.imshow(HamamatsuCrop)
plt.subplot(153)
plt.title('Averaged edge response')
plt.plot(ERIResponse, c=Colors[0], label='ERI')
plt.plot(HamamatsuResponse, c=Colors[1], label='Hamamatsu')
# Plot some (non-averaged) edge responses, too
for ctr, line in enumerate(range(100, 800, 200)):
    plt.subplot(252)
    plt.axhline(line, c=Colors[ctr+2])
    plt.subplot(257)
    plt.axhline(line, c=Colors[ctr+2])
    plt.subplot(153)
    plt.plot(ERICrop[line, :], alpha=0.309, c=Colors[ctr+2])
    plt.plot(HamamatsuCrop[line, :], alpha=0.309, c=Colors[ctr+2])
plt.legend(loc='lower right')

# Calculate MTF.
# According to http://www.imatest.com/docs/validating_slanted_edge/, the MTF is
# the Fourier transform of the line spread function, which is the derivative of
# the averaged edge.
# We thus calculate the average edge ($source$Response) and take the derivative
# of this (with the `LSF` function, which uses `numpy.diff`).
# To the derivative we fit a gaussian function with the `gaussianfit` function
# which then acts as an input for the `MTF` function above.
plt.subplot(154)
plt.title('Line spread function')
plt.plot(LSF(ERIResponse), c=Colors[2], alpha=0.5, label='ERI Data')
plt.plot(LSF(HamamatsuResponse), c=Colors[3], alpha=0.5, label='Hamamatsu Data')
plt.plot(gaussianfit(LSF(ERIResponse)), c=Colors[0], label='ERI fit')
plt.plot(gaussianfit(LSF(HamamatsuResponse)), c=Colors[1], label='Hamamatsu fit')
plt.legend(loc='best')
plt.subplot(155)
plt.plot(MTF(gaussianfit(LSF(ERIResponse))), c=Colors[0],
         label='MTF ERI')
plt.plot(MTF(gaussianfit(LSF(HamamatsuResponse))), c=Colors[1],
         label='MTF Hamamatsu')
plt.legend(loc='best')
plt.show()
