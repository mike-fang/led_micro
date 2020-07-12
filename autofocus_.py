from ximea_pkg.ximea import xiapi
import cv2
import time
import numpy as np
from asi_controller import AsiController

def sharpness(img):
    gy, gx = np.gradient(img)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharpness = np.average(gnorm)
    return sharpness

control = AsiController(config_file='./asi_config.yml', init_xy=False)

#create instance for first connected camera 
cam = xiapi.Camera()

#start communication
print('Opening first camera...')
cam.open_device()

#settings
#cam.set_exposure(1_000_000)
#cam.set_exposure(20_000)
exposure = 500_000
cam.set_exposure(exposure)

#create instance of Image to store image data and metadata
img = xiapi.Image()

#start data acquisition
print('Starting data acquisition...')
cam.start_acquisition()
interp=False
prev_sharp = None
dir = +1
try:
    print('Starting video. Press \'q\' to exit.')
    t0 = time.time()
    while True:
        #get data and pass them from camera to img
        cam.get_image(img)

        #create numpy array with data from camera. Dimensions of the array are 
        #determined by imgdataformat
        data = img.get_image_data_numpy()[2::5, ::5]


        if prev_sharp is None:
            prev_sharp = sharpness

        delta_sharp = sharpness - prev_sharp
        prev_sharp = sharpness

        if control.where_z() < 0:
            if delta_sharp < 0:
                dir *= -1
            if dir == +1:
                control.cmd('r z=+10')
            else:
                control.cmd('r z=-10')

        #show acquired image with time since the beginning of acquisition
        key_press = cv2.waitKey(1)
        if key_press & 0xFF == ord('q'):
            break
        cv2.imshow('Hypercamcam', data)

        
except KeyboardInterrupt:
    cv2.destroyAllWindows()

#stop data acquisition
print('Stopping acquisition...')
cam.stop_acquisition()

#stop communication
cam.close_device()

print('Done.')
