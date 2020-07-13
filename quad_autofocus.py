from elp_usb_cam import ELP_Camera
from capture_msi import init_rb, STD_EXPOSURE
import numpy as np
from asi_controller import AsiController
from time import time, sleep
from parabolic_optim import QuadOptim, GradOptim
from get_sharpness import get_mean_log_power
import cv2

def grad_sharp(img):
    if len(img.shape) == 3:
        img = img.mean(axis=2)
    gy, gx = np.gradient(img)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharpness = np.average(gnorm)
    return sharpness

# init
cam = ELP_Camera(0)
cam.set_exp(300)
rb = init_rb()
control = AsiController(config_file='./asi_config.yml', init_xy=False)

# turn on white led
state = np.zeros(8)
state[7] = 1
rb.set_state(state)

# sharpness criterion
def eval_sharp():
    for _ in range(3):
        frame = cam.capture_img()
    #sharpness = get_mean_log_power(frame, exp=1)
    sharpness = grad_sharp(frame)
    print(f'sharpness = {sharpness:.4f}')
    return sharpness

# init optimizer
limits = [-30, 30]
max_step = 5.
optimizer = QuadOptim(limits=limits, max_step=max_step, stage_control=control, eval_sharp=eval_sharp, n_init=5, n_fit=5)
optimizer.init_measurements()

AUTO = True
dz = 0
while True:
    frame = cam.capture_img()
    if AUTO:
        optimizer.step()
        #optimizer.plot()
    cv2.imshow('', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
