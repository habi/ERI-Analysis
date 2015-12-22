"""
PlotVoltageVsCurrent.py | David Haberthuer <david.haberthuer@psi.ch>

We acquired images with the ERI source. We can only set the voltage,
the current is given by the power supply. This script plots the relation of
both values, which are recorded in the file names.
And it also plots the combinations we acquired for the Hamamatsu source
"""

import os
import glob
import matplotlib.pylab as plt

# Wider default curves, better markers and grid
plt.rc('lines', linewidth=2, marker='o')
plt.rc('axes', grid=True)

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')
# Get all folders in StartPath and ask user which one we should plot
Folders = glob.glob(os.path.join(StartPath, '*'))
for counter, FolderToPlot in enumerate(Folders):
    ImageList = glob.glob(os.path.join(FolderToPlot, '*.raw'))

    print '%s/%s: Reading values from %s images in folder ' \
          '%s' % (counter + 1, len(Folders), len(ImageList),
                  os.path.basename(FolderToPlot))
    Voltage = [int(os.path.basename(image).split('_')[1][:-2]) for image in
               ImageList]
    Current = [int(os.path.basename(image).split('_')[2][:-2]) for image in
               ImageList]
    plt.scatter(Voltage, Current, label=os.path.basename(FolderToPlot))
    plt.xlabel('Voltage [kV]')
    plt.ylabel('Current [uA]')
    plt.legend(loc='best')
    plt.ylim(ymin=0)
    plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                             'ERI-Analysis', 'Images',
                             'VoltageVsCurrent_' +
                             os.path.basename(FolderToPlot) + '.png'))
    plt.xlim([0, 75])
    plt.ylim([0, 75])
    plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                             'ERI-Analysis', 'Images',
                             'VoltageVsCurrent_' +
                             os.path.basename(FolderToPlot) + '_Detail.png'))
    plt.show()
