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

StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry', 'Images')

HamamatsuFolders = glob.glob(os.path.join(StartPath, 'Hamamatsu*'))
ERIFolders = glob.glob(os.path.join(StartPath, 'ERI*'))

# Colors from 'I want hue!'
colors = ["#82DFB2",
          "#DAB5D6",
          "#E9AD71",
          "#8DD6DF",
          "#D8D56D",
          "#A4E280"]

plt.figure(figsize=[16, 9])
# for counter, folder in enumerate(HamamatsuFolders):
#     print 'Reading folder %s: %s' % (counter, os.path.basename(folder))
#     ImageList = glob.glob(os.path.join(StartPath, folder, '*.raw'))
#     Voltage = [int(os.path.basename(image).split('_')[1][:-2]) for image in
#                ImageList]
#     Current = [int(os.path.basename(image).split('_')[2][:-2]) for image in
#                ImageList]
#     plt.scatter(Voltage, Current, label=os.path.basename(folder),
#                 c=colors[counter], alpha=0.5)

for counter, folder in enumerate(ERIFolders):
    print 'Reading folder %s: %s' % (counter + len(ERIFolders),
                                     os.path.basename(folder))
    ImageList = glob.glob(os.path.join(StartPath, folder, '*.raw'))
    Voltage = [int(os.path.basename(image).split('_')[1][:-2]) for image in
               ImageList]
    Current = [int(os.path.basename(image).split('_')[2][:-2]) + 5 * counter
               for image in ImageList]
    plt.scatter(Voltage, Current, label=os.path.basename(folder),
                c=colors[counter+len(ERIFolders)])


plt.xlabel('Voltage [kV]')
plt.ylabel('Current [uA]')
plt.legend(loc='best')
plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                         'ERI-Analysis', 'VoltageVsCurrentSpread.png'))
plt.xlim([25, 60])
plt.ylim([0, 50])
plt.savefig(os.path.join(os.path.expanduser('~'), 'Data20', 'CNT',
                         'ERI-Analysis', 'VoltageVsCurrent.png'))
plt.show()
