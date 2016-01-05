"""
PlotVoltageVsCurrent.py | David Haberthuer <david.haberthuer@psi.ch>

We acquired images with the ERI source. We can only set the voltage,
the current is given by the power supply. From looking at the data we seem to
see an exponential connection. This script fits the curves.
"""

import os
import glob
import matplotlib.pylab as plt
import numpy
import scipy.optimize
import scipy.stats


def fitting_function(x, a, b, c):
    return a * numpy.exp(b * x) + c


def rand_jitter(arr):
    """
    Jitter data to avoid overlapping data points.
    Based on http://stackoverflow.com/a/21276920/323100
    """
    stdev = .005*(max(arr)-min(arr))
    return arr + numpy.random.randn(len(arr)) * stdev

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ERIFolders = sorted(glob.glob(os.path.join(StartPath, 'ERI*')))

# Colors from 'I want hue!'
colors = ["#BEDB87",
          "#D5B2E6",
          "#8AD5E1",
          "#ECAC68",
          "#F2A2A8",
          "#5FE3BF",
          "#E2D75E",
          "#A7D8AF",
          "#87E38F",
          "#C0E86A",
          "#D6C276",
          "#CFC2DB"]
# Wider default curves, better markers and grid
plt.rc('lines', linewidth=2, marker='o')
plt.rc('axes', grid=True)

# Grab all images and plot values for folders
ImageList = []
AllImages = []
plt.figure(figsize=[16, 9])
for counter, folder in enumerate(ERIFolders):
    print 'Reading values from folder %s/%s: %s' % (counter + 1,
                                                    len(ERIFolders),
                                                    os.path.basename(folder))
    ImageList = sorted(glob.glob(os.path.join(StartPath, folder, '*.raw')))
    AllImages += ImageList
    Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                           image in ImageList])
    Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                           image in ImageList])
    plt.scatter(rand_jitter(Voltage), rand_jitter(Current), c=colors[counter],
                label=os.path.basename(folder))
# Exponential fit for *all* images
InitialGuess = (0.05, 1e-1, 10)
Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                       image in AllImages])
Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                       image in AllImages])
try:
    try:
        OptimalValues, Covariance = scipy.optimize.curve_fit(fitting_function,
                                                             Voltage[:-1],
                                                             Current[:-1],
                                                             p0=InitialGuess)
        print '\tThe best exponential fit to the data is %0.2e * ' \
              'numpy.exp(%0.2e * x) + %0.2e' % (OptimalValues[0],
                                                OptimalValues[1],
                                                OptimalValues[2])
        plt.plot(sorted(Voltage),
                 sorted(fitting_function(Voltage, *OptimalValues)), 'k-',
                 label='Fitted Curve (%0.2f*e^%0.2e*x+%0.2f)' % (
                OptimalValues[0], OptimalValues[1], OptimalValues[2]))
    except RuntimeError:
        print 'No optimal exponential fit parameters found'
except AttributeError:
    exit('You need to "module load xbl/epd" to make this script work\nAs a '
         'consequence, the script cannot be run in PyCharm, but has to be run '
         'in the terminal...')
ManualFit = [InitialGuess[0] * numpy.exp(InitialGuess[1] * i) +
             InitialGuess[2] for i in Voltage]
plt.plot(sorted(Voltage), sorted(ManualFit), 'k--',
         label='Empirical fit (%0.2f*e^%0.2e*x+%0.2f)' % (InitialGuess[0],
                                                          InitialGuess[1],
                                                          InitialGuess[2]))
plt.xlabel('Voltage [kV]')
plt.ylabel('Current [uA]')
plt.xlim([20, 70])
plt.ylim([0, 60])
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                         'ERI-Analysis', 'Images', 'ExponentialFit.png'))
plt.show()
