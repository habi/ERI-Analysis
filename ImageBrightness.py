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

from ERIfunctions import *

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
