from elp_usb_cam import ELP_Camera
from capture_msi import init_rb, STD_EXPOSURE
import numpy as np
from asi_controller import AsiController
from time import time, sleep
from get_sharpness import grad_sharp
import cv2
import matplotlib.pylab as plt

def get_sharpness(img):
    
    gy, gx = np.gradient(img)
    gnorm = np.sqrt(gx**2 + gy**2)
    sharpness = np.average(gnorm)
    return sharpness

# init
cam = ELP_Camera(0)
rb = init_rb()
control = AsiController(config_file='./asi_config.yml', init_xy=False)


class AutoFocus:
    def __init__(self, cam, rb, control, rng=10, steps=20):
        self.cam = cam
        self.rb = rb
        self.stage = control
        self.rng = rng
        self.steps = steps
    def scan(self, z0, rng, steps):
        z_scan = np.linspace(z0-rng, z0+rng, steps)
        sharp_scan = np.zeros_like(z_scan)
        for n, z in enumerate(z_scan):
            self.stage.goto_z(z)
            sleep(.5)
            for _ in range(5):
                frame = cam.capture_img()
                sharp = grad_sharp(frame)
                sharp_scan[n] = sharp
            print(z)
            print(sharp)
        
        return z_scan, sharp_scan
    def step(self, iter=1):
        # turn on white led
        state = np.zeros(8)
        state[7] = 1
        self.rb.set_state(state)
        
        rng = self.rng
        steps = self.steps
        for i in range(iter):
            z0 = self.stage.where_z()
            Z, S = self.scan(z0, rng, steps)
            z0 = Z[S.argmax()]
            rng /= 5
            self.stage.goto_z(z0)
            sleep(1.)
        
        # turn off leds
        state = np.zeros(8)
        self.rb.set_state(state)
        
        
rng=10
steps=10
af = AutoFocus(cam, rb, control, rng=rng, steps=steps)

af.step(iter=1)
plt.imshow(cam.capture_img())
plt.show()
