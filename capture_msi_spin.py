from ft245r import relay_ft245r
from ft245r.relay_ft245r import FT245R
import sys
from time import sleep
import numpy as np
from spin_spin import Stepper
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *
import cv2
import os
from led_controller import LED_Controller

def init_rb():
    rb = FT245R()
    dev_list = rb.list_dev()

    if len(dev_list) == 0:
        print('No FT245R devices found')
        sys.exit()
        
    dev = dev_list[0]
    print('Using device with serial number ' + str(dev.serial_number))
    rb.connect(dev)

    return rb

def capture_ms_img(cam, rb, stepper, exposures=None, n_leds=8, pause=0):
    led_control = LED_Controller(rb, stepper)
    H, W, n_channels = cam.img_shape
    ms_img = np.zeros((H, W, n_channels*n_leds), dtype=np.uint8)
    cam.set_auto_wb(False)
    state = np.zeros(8)
    state[4] = 1    
    rb.set_state(state)
    stepper.engage()
    for n in range(n_leds):
        stepper.goto_filter(n)
        if exposures is not None:
            try:
                cam.set_exp(exposures[n])
            except:
                cam.set_exp(exposures)
        sleep(pause)
        for _ in range(10):
            img = cam.capture_img()
        print(img.mean())
        ms_img[:, :, n*n_channels:(n+1)*n_channels] = img
    stepper.disengage()
    rb.set_state(np.zeros(8))
    return ms_img

def get_exposures(cam, rb, n_leds=8, pause=.5, target=128, tol=10, n_iter=20):
    exposures = []
    
    for n in range(n_leds):
        # Turn on nth led
        state = np.zeros(n_leds)
        state[n] = 1
        rb.set_state(state)
        sleep(pause)

        high = 5000
        low = 0
        for _ in range(n_iter):
            exposure = (high + low)/2.
            if high - low < 10:
                break
            cam.set_exp(exposure)
            for _ in range(5):
                img = cam.capture_img()

            mean_lum = img.mean()
            if mean_lum < target - tol:
                print(f'too low -- mean lum: {mean_lum:.2f}, high: {high:.2f}, low: {low:.2f}')
                low = exposure
            elif mean_lum > target + tol:
                print(f'too high -- mean lum: {mean_lum:.2f}, high: {high:.2f}, low: {low:.2f}')
                high = exposure
            else:
                print(f'good enough -- mean lum: {mean_lum:.2f}, high: {high:.2f}, low: {low:.2f}')
                break
        exposures.append(exposure)
    rb.set_state(np.zeros(n_leds))
    return np.array(exposures)

if __name__ == '__main__':
    cam = ELP_Camera(0)
    rb = init_rb()
    #exposures = get_exposures(cam, rb, n_leds=5, pause=.5, target=75,tol=5)
    #np.save('./exposures.npy', exposures)
    stepper = Stepper(config_file='spinspin_config.json', pulse_time=0.0005)
    ms_img = capture_ms_img(cam, rb, stepper, n_leds=4, exposures=None, pause=.5)
    for n in range(4):
        plt.figure(figsize=(10, 6))
        plt.imshow(ms_img[:, :, n*3:(n+1)*3])
    plt.show()  
