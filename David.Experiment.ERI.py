# -*- coding: utf-8 -*-

"""
David.Experiment.ERI.py | David Haberthür <david.haberthuer@psi.ch>

Script file to snap images with different kV and uA settings of the ERI x-ray
source.
"""

# Imports
from gantry_control import *
import glob
import logging
import random

# Setup
StartPath = os.path.join(os.path.expanduser('~'), 'Data20', 'Gantry')

testing = False

# Experimental settings
Voltages = list(range(25, 65, 1))
# Randomize voltages to exclude hysteresis
random.shuffle(Voltages)
DetectorExposureTime = 30  # Seconds, converted to when setting the detector

# Check if we already have files in the designated directory. If we do,
# then do not run the script.
files = glob.glob(os.path.join(StartPath, 'ERI', '*.raw'))
if files:
    exit('Remove the %s .raw files in %s before running this script' %
         (len(files), os.path.join(StartPath, 'ERI')))

# Set up logging
LogFileName = os.path.join(StartPath, 'ERI', 'ERI.log')
log = logging.getLogger(LogFileName)
log.setLevel(logging.INFO)
handler = logging.FileHandler(LogFileName, 'w')
log.addHandler(handler)

# Start Experiment
log.info('Experiment started at %s', time.strftime('%d.%m.%Y at %H:%M:%S'))
log.info(80 * '-')

# Start the detector
print 'Starting the ShadoBox detector'
# Check if we have the camera here
if not sb.is_camera_on():
    sb.start()
# Set exposure time
sb.set_exposure_time(DetectorExposureTime * 1000)

if not testing:
    print 'Start the ERI source now.'
    ERIStart = raw_input('Press "Enter" once you are done')
    log.info('Source started at %s', time.strftime('%d.%m.%Y at %H:%M:%S'))

# Log experiment conditions
log.info('Source voltage will be set from %s kV to %s kV in %s steps.',
         min(Voltages), max(Voltages), len(Voltages))
log.info('Source current will be entered manually')
log.info(80 * '-')

for v, voltage in enumerate(Voltages):
    print 80 * '-'
    current = 0
    while not current:
        try:
            current = int(raw_input('Set source voltage to %s kV and input'
                                    ' the current shown on the ERI power '
                                    'supply [uA]: ' % voltage))
        except ValueError:
            print('Try inputting an integer number...')
    print '%s | %s/%s | %s kV/%s uA | %s' % ('ERI', v + 1, len(Voltages),
                                             voltage, current,
                                             time.strftime(
                                                 '%d.%m.%Y at %H:%M:%S'))
    OutPutPath = os.path.join(StartPath, 'ERI')
    try:
        os.makedirs(OutPutPath)
    except OSError:
        pass
    if not testing:
        sleepytime = 5
        print 'Waiting for %s seconds until the source has settled...' % \
              sleepytime
        time.sleep(sleepytime)

    sb.set_directory(OutPutPath)
    ImagePrefix = '%s_%03dkV_%03duA_%ssExp' % ('ERI', voltage, current,
                                               DetectorExposureTime)
    sb.set_prefix(ImagePrefix)
    print 'Acquiring image for %s seconds' % DetectorExposureTime
    sb.acquire(1, 2)
    log.info('Image %s/%s (%s) acquired at %s', v + 1, len(Voltages),
             ImagePrefix + '.raw', time.strftime('%d.%m.%Y at %H:%M:%S'))
    print 'Saved image as %s_01' % ImagePrefix

# Close log file
log.info(80 * '-')
log.info('Experiment finished at %s', time.strftime('%d.%m.%Y at %H:%M:%S'))
handler.close()

# Turn off the source
if not testing:
    print 'Turn off the ERI source now.'

print 80 * '-'
print 'Closing connection to ShadoBox.'
if not testing:
    sb.stop()
    sb.disconnect()
logging.shutdown()
print 'Done with everything.'
