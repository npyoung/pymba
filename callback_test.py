from pymba import *
import time
import numpy as np

# start Vimba
vimba = Vimba()
vimba.startup()

# get system object
system = vimba.getSystem()

# list available cameras (after enabling discovery for GigE cameras)
if system.GeVTLIsPresent:
    system.runFeatureCommand("GeVDiscoveryAllOnce")
    time.sleep(0.2)
cameraIds = vimba.getCameraIds()

# get and open a camera
camera0 = vimba.getCamera(cameraIds[0])
camera0.openCamera()

# set the value of a feature
camera0.AcquisitionMode = 'SingleFrame'

# create new frames for the camera
frame0 = camera0.getFrame()    # creates a frame

# announce frame
frame0.announceFrame()

from Queue import Queue
out_frames = Queue()

def mycb(frame_ptr):
    frame = np.ndarray(buffer=frame0.getBufferByteData(),
                       dtype=np.uint8,
                       shape=(frame0.height, frame0.width))
    out_frames.put(frame)

from pymba.vimbadll import VimbaDLL
frame_callback = VimbaDLL.frameDoneCallback(mycb)

# capture a camera image
camera0.startCapture()
frame0.queueFrameCapture(callback=frame_callback)
camera0.runFeatureCommand('AcquisitionStart')
camera0.runFeatureCommand('AcquisitionStop')
frame0.waitFrameCapture()

# get image data...
imgData = frame0.getBufferByteData()

# ...or use NumPy for fast image display (for use with OpenCV, etc)
import numpy as np
moreUsefulImgData = np.ndarray(buffer = frame0.getBufferByteData(),
                               dtype = np.uint8,
                               shape = (frame0.height,
                                        frame0.width,
                                        1))

# clean up after capture
camera0.endCapture()
camera0.revokeAllFrames()

# close camera
camera0.closeCamera()

# shutdown Vimba
vimba.shutdown()

import matplotlib.pyplot as plt
plt.imshow(out_frames.get(), cmap='hot')
plt.show()
