from elp_usb_cam import ELP_Camera
from capture_msi import init_rb, STD_EXPOSURE
import numpy as np
from asi_controller import AsiController
from time import time, sleep
import cv2

def get_sharpness(img):
    gy, gx = np.gradient(img)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharpness = np.average(gnorm)
    return sharpness

# init
cam = ELP_Camera(0)
rb = init_rb()
control = AsiController(config_file='./asi_config.yml', init_xy=False)

# turn on white led
state = np.zeros(8)
state[7] = 1
rb.set_state(state)

prev_sharp = 0
dz = 2.5

AUTO = True
while True:
    frame = cam.capture_img()
    mean_img = frame.mean(axis=2)
    sharpness = get_sharpness(mean_img)
    if (sharpness < prev_sharp) and (prev_sharp < prev2_sharp):
        dz *= -1
        print('Switch')
    prev2_sharp = prev_sharp
    prev_sharp = sharpness
    if AUTO:
        control.move_relative_z(dz) 
    print(f'Sharpness: {sharpness:.4f} Z: {control.where_z():.4f}')
    cv2.imshow('', frame)
    if AUTO:
        sleep(3)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
