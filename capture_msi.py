from ft245r import relay_ft245r
from ft245r.relay_ft245r import FT245R
import sys
from time import sleep
import numpy as np
import matplotlib.pylab as plt
import cv2
import os

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


def capture_ms_img(cam, n_leds=8, pause=0, vc_channel=1):
    rb = init_rb()
    H, W, n_channels = cam.img_shape
    ms_img = np.zeros((H, W, n_channels*n_leds))
    for n in range(n_leds):
        state = np.zeros(n_leds)
        state[n] = 1
        rb.set_state(state)
        sleep(pause)
        ms_img[:, :, n*n_channels:(n+1)*n_channels] = cam.capture_img()
    rb.set_state(np.zeros(n_leds))
    return ms_img

if __name__ == '__main__':
    cam = cv2.VideoCapture(1)
    _, _ = cam.read()
    cam.set(cv2.CAP_PROP_SETTINGS, 1)
    cam.set(cv2.CAP_PROP_GAIN, 1)
    print(cam.get(cv2.CAP_PROP_GAIN))
        

    assert False
    ms_img = capture_ms_img(n_leds=8, pause=.0)

    for n in range(24):
        plt.subplot(4, 6, n+1)
        plt.imshow(ms_img[:, :, n], cmap='Greys_r')
        plt.xticks([])
        plt.yticks([])
    plt.show()
