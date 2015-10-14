# -*- coding: utf-8 -*-

"""
David.Experiment.Hamamatsu.py | David Haberthür <david.haberthuer@psi.ch>

Script file to snap images with different kV and uA settings of the Hamamatsu
x-ray source.
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
Voltages = range(25, 65, 1)
Currents = range(10, 201, 5)
# Randomize voltages and currents to exclude hysteresis
random.shuffle(Voltages)
random.shuffle(Currents)
DetectorExposureTime = 15  # Seconds, converted to when setting the detector

# Check if we already have files in the designated directory. If we do,
# then do not run the script.
files = glob.glob(os.path.join(StartPath, 'Hamamatsu', '*.raw'))
if files:
    exit('Remove the %s .raw files in %s before running this script' %
         (len(files), os.path.join(StartPath, 'Hamamatsu')))

# Set up logging
LogFileName = os.path.join(StartPath, 'Hamamatsu', 'Hamamatsu.log')
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
    print 'Starting the Hamamatsu tube'
    # Start the source with some moderate settings and let it run for five
    # hours to stabilize
    tube.open_port()
    tube.start()
    tube.on()
    tube.set_voltage(50)
    tube.set_current(50)
    log.info('Started Hamamatsu source at %s',
             time.strftime('%d.%m.%Y at %H:%M:%S'))
    print 'Waiting for 5 hours until source stabilized'
    finishtime = time.time() + 5 * 60 * 60
    print 'Will continue on %s' % time.strftime('%d.%m.%Y at %H:%M:%S',
                                                time.gmtime(finishtime))
    time.sleep(5 * 60 * 60)
    log.info('Source stabilization completed at %s',
             time.strftime('%d.%m.%Y at %H:%M:%S'))

# Log experiment conditions
log.info('Source voltage will be set from %s kV to %s kV in %s steps.',
         min(Voltages), max(Voltages), len(Voltages))
log.info('Source current will be set from %s uA to %s uA in %s steps.',
         min(Currents), max(Currents), len(Currents))
log.info(80 * '-')

for v, voltage in enumerate(Voltages):
    for c, current in enumerate(Currents):
        print 80 * '-'
        print '%s | %s/%s | %s kV/%s uA' % ('Hamamatsu', (v + 1) * (c + 1),
                                            len(Voltages) * len(Currents),
                                            voltage, current)
        # Only use the settings that the Hamamatsu source is able to do
        # so according to its data sheet
        if voltage < 40 and current > 100:
            print 'According to the data sheet of the Hamamtsu source, ' \
                  'we cannot operate it safely at %s kV and %s uA' % (
                voltage, current)
            print 'Skipping this setting...'
        else:
            OutPutPath = os.path.join(StartPath, 'Hamamatsu')
            try:
                os.makedirs(OutPutPath)
            except OSError:
                pass
            if not testing:
                sleepytime = 5
                print 'Setting tube to %s kV and %s uA and waiting for %s ' \
                      'seconds until it has settled...' % (voltage, current,
                                                           sleepytime)
                tube.set_voltage(voltage)
                tube.set_current(current)
                time.sleep(sleepytime)

            sb.set_directory(OutPutPath)
            ImagePrefix = '%s_%03dkV_%03duA_%ssExp' % ('Hamamatsu', voltage,
                                                       current,
                                                       DetectorExposureTime)
            sb.set_prefix(ImagePrefix)
            print 'Acquiring image for %s seconds' % DetectorExposureTime
            sb.acquire(1, 2)
            log.info('Image %s/%s (%s) acquired at %s', (v + 1) * (c + 1),
                     len(Voltages) * len(Currents),ImagePrefix + '.raw',
                     time.strftime('%d.%m.%Y at %H:%M:%S'))
            print 'Saved image as %s_01' % ImagePrefix

# Close log file
log.info(80 * '-')
log.info('Experiment finished at %s', time.strftime('%d.%m.%Y at %H:%M:%S'))
handler.close()

# Turn off the source
if not testing:
    print 'Turning off the Hamamatsu source.'
    tube.off()
    tube.stop()

print 80 * '-'
print 'Closing connection to ShadoBox.'
if not testing:
    sb.stop()
    sb.disconnect()
logging.shutdown()
print 'Done with everything.'
