import cv2
import numpy as np
from datetime import datetime
from capture_msi import capture_ms_img, init_rb
import os, time
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *


def start_time_lapse(dt, tmax, out_path, save_thumbnail=False):
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    cam = ELP_Camera(1)
    t0 = time.time()
    rb = init_rb()
    while time.time() - t0 < tmax:
        start_time = time.time()
        ms_img = capture_ms_img(cam, rb, pause=.5)
        time_stamp = f'{time.time():.2f}'.replace('.', '_')
        np.save(os.path.join(out_path, f'{time_stamp}.npy'), ms_img)
        if save_thumbnail:
            show_rgb_comp(ms_img)
            plt.savefig(os.path.join(out_path, f'{time_stamp}.png'))
        end_time = time.time()
        time_elapsed = end_time - start_time
        sleep_time = dt - time_elapsed
        if sleep_time < 0:
            print(f'Warning, capture time longer than time lapse requirements')
        else:
            time.sleep(sleep_time)


if __name__ == '__main__':
    CUR_DIR = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join('results', 'test')
    start_time_lapse(5, 20, out_path, save_thumbnail=True)
