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

def camera_test(cam):
    cam.set(cv2.CAP_PROP_GAIN, -8)
    while True:
        ret, frame = cam.read()
        cv2.imshow('', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()

def capture_ms_img(n_leds, pause, vc_channel=1):
    rb = init_rb()
    cam = cv2.VideoCapture(vc_channel)

    ret, frame = cam.read()
    H, W, n_channels = frame.shape
    ms_img = np.zeros((H, W, n_channels*n_leds))
    for n in range(n_leds):
        state = np.zeros(n_leds)
        state[n] = 1
        rb.set_state(state)
        ret, frame = cam.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ms_img[:, :, n*n_channels:(n+1)*n_channels] = frame
        sleep(pause)
    rb.set_state(np.zeros(n_leds))
    return ms_img

if __name__ == '__main__':
    cam = cv2.VideoCapture(1)
    cam.set(cv2.CAP_PROP_GAIN, -8)
    camera_test(cam)
    assert False
    ms_img = capture_ms_img(n_leds=8, pause=.0)

    for n in range(24):
        plt.subplot(4, 6, n+1)
        plt.imshow(ms_img[:, :, n], cmap='Greys_r')
        plt.xticks([])
        plt.yticks([])
    plt.show()
