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
try:
    # import scipy.optimize
    import scipy.stats
except ImportError:
    print 'To use this script, we need to load the Enthought Python ' \
          'distribution. To do so, please enter the command below into the ' \
          'terminal and restart the script.\n'
    print 'module load xbl/epd\n'
    exit()

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
ERIFolders = glob.glob(os.path.join(StartPath, 'ERI*'))

# Colors from 'I want hue!'
colors = ["#82DFB2",
          "#DAB5D6",
          "#E9AD71",
          "#8DD6DF",
          "#D8D56D",
          "#A4E280"]


def fitting_function(x, a, b, c):
    return a * numpy.exp(b * x) + c

plt.figure(figsize=[15, 15])
for counter, folder in enumerate(ERIFolders):
    plt.subplot(3, 1, counter+1)
    plt.title(folder)
    print 'Reading images from folder %s: %s' % (counter + 1,
                                                 os.path.basename(folder))
    ImageList = sorted(glob.glob(os.path.join(StartPath, folder, '*.raw')))
    Voltage = numpy.array([int(os.path.basename(image).split('_')[1][:-2]) for
                           image in ImageList])
    Current = numpy.array([int(os.path.basename(image).split('_')[2][:-2]) for
                           image in ImageList])
    plt.scatter(Voltage, Current, label=os.path.basename(folder),
                c=colors[counter+len(ERIFolders)])
    InitialGuess =(0.07, 0.095, 9.5)
    OptimalValues, Covariance = scipy.optimize.curve_fit(fitting_function,
                                                         Voltage, Current,
                                                         p0=InitialGuess)
    print '\tThe best exponential fit to the data is %s * numpy.exp(%s * x) ' \
          '+ %s' % (OptimalValues[0], OptimalValues[1], OptimalValues[2])
    plt.plot(Voltage, fitting_function(Voltage, *OptimalValues), 'r-',
             label='Fitted Curve (%0.2f*e^%0.2e*x+%0.2f)' % (OptimalValues[0],
                                                             OptimalValues[1],
                                                             OptimalValues[2]))
    ManualFit = [InitialGuess[0] * numpy.exp(InitialGuess[1] * i) +
                 InitialGuess[2] for i in Voltage]
    plt.plot(Voltage, ManualFit, 'g-',
             label='Empirical fit (%0.2f*e^%0.2e*x+%0.2f)' % (InitialGuess[0],
                                                              InitialGuess[1],
                                                              InitialGuess[2]))
    plt.xlabel('Voltage [kV]')
    plt.ylabel('Current [uA]')
    plt.xlim([0, 66])
    plt.ylim(ymin=0)
    plt.legend(loc='best')
plt.show()
