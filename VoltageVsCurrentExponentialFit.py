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

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ERIFolders = glob.glob(os.path.join(StartPath, 'ERI*'))

# Colors from 'I want hue!'
colors = ["#80DEC3", "#E8B172", "#CBBCDC", "#C1DD79"]
# Wider default curves, better markers and grid
plt.rc('lines', linewidth=2, marker='o')
plt.rc('axes', grid=True)


def fitting_function(x, a, b, c):
    return a * numpy.exp(b * x) + c

# Grab all images and plot values for folders
ImageList = []
plt.figure(figsize=[16,9])
for counter, folder in enumerate(ERIFolders[:-1]):
    print 'Reading values from folder %s: %s' % (counter + 1,
                                                 os.path.basename(folder))
    ImageList += sorted(glob.glob(os.path.join(StartPath, folder, '*.raw')))
    Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                           image in ImageList])
    Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                           image in ImageList])
    plt.scatter(Voltage, Current, c=colors[counter], alpha=0.618,
                label=os.path.basename(folder))
# Extract all values
Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                       image in ImageList])
Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                       image in ImageList])

# Exponential fit
InitialGuess = (0.05, 1e-1, 10)
try:
    OptimalValues, Covariance = scipy.optimize.curve_fit(fitting_function,
                                                         Voltage[:-1],
                                                         Current[:-1],
                                                         p0=InitialGuess)
except AttributeError:
    exit('You need to "module load xbl/epd" to make this script work\nAs a '
         'consequence, the script cannot be run in PyCharm, but has to be run'
         'in the terminal...')
print '\tThe best exponential fit to the data is %0.2e * numpy.exp(%0.2e * x) ' \
      '+ %0.2e' % (OptimalValues[0], OptimalValues[1], OptimalValues[2])
plt.plot(sorted(Voltage), sorted(fitting_function(Voltage, *OptimalValues)),
         '-', c=colors[2], label='Fitted Curve (%0.2f*e^%0.2e*x+%0.2f)' % (
        OptimalValues[0], OptimalValues[1], OptimalValues[2]))
ManualFit = [InitialGuess[0] * numpy.exp(InitialGuess[1] * i) +
             InitialGuess[2] for i in Voltage]
plt.plot(sorted(Voltage), sorted(ManualFit), '-', c=colors[3],
         label='Empirical fit (%0.2f*e^%0.2e*x+%0.2f)' % (InitialGuess[0],
                                                          InitialGuess[1],
                                                          InitialGuess[2]))
plt.xlabel('Voltage [kV]')
plt.ylabel('Current [uA]')
plt.xlim([20, 70])
plt.ylim(ymin=0)
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                         'ERI-Analysis', 'Images', 'ExponentialFit.png'))
plt.show()
