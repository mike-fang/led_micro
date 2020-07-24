import cv2
import numpy as np
from datetime import datetime
from capture_msi import init_rb
from capture_msi import capture_ms_img as relay_capture
from capture_msi_stepper import capture_ms_img as stepper_capture
from stepper_control import Stepper
from spin_spin import Stepper as SpinSpin
import os, time
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *
import argparse


def start_time_lapse(dt, tmax, out_path, capt='stepper', exposures=None, save_thumbnail=False):
    if not os.path.isdir(out_path):
        os.makedirs(out_path)
    cam = ELP_Camera(0)
    t0 = time.time()
    rb = init_rb()
    if capt == 'stepper':
        stepper = Stepper(pulse_time=0.00050)
    while time.time() - t0 < tmax:
        start_time = time.time()
        if capt == 'stepper':
            ms_img = stepper_capture(cam, rb, stepper, n_leds=5, exposures=exposures)
        elif capt == 'relay':
            ms_img = relay_capture(cam, rb, n_leds=8, exposures=exposures)
        time_stamp = f'{time.time():.2f}'.replace('.', '_')
        np.save(os.path.join(out_path, f'{time_stamp}.npy'), ms_img)
        if save_thumbnail:
            plt.figure()
            show_rgb_comp(ms_img)
            plt.savefig(os.path.join(out_path, f'{time_stamp}_tn.png'))
            cv2.imwrite(os.path.join(out_path, f'{time_stamp}_white.png'), ms_img[:, :, -1])
            plt.clear()
            plt.clf()
            plt.cla()
        end_time = time.time()
        time_elapsed = end_time - start_time
        sleep_time = dt - time_elapsed
        if sleep_time < 0:
            print(dt, time_elapsed)
            print(f'Warning, capture time longer than time lapse requirements')
        else:
            time.sleep(sleep_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', nargs=1, default='test', help='Directory to save data collected')
    parser.add_argument('--dt', help='Time before each capture in minutes')
    parser.add_argument('--tmax', help='Duration of time-lapse in minutes')
    parser.add_argument('--stepper', help='Using stepper motor', action='store_true')

    args = parser.parse_args()

    CUR_DIR = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join('results', args.dir[0])

    dt = float(args.dt) * 60
    tmax = float(args.tmax) * 60
    capt = 'stepper' if args.stepper else 'relay'
    #exposures = np.load('./exposures.npy')
    exposures = None
    print('Starting time-lapse capture...')
    print(f'  Time between capture {dt / 60:.2f} mins')
    print(f'  Total time of cpature {tmax / 60:.2f} mins')
    print(f'  Output saved to {out_path}')
    print(f'  Using {capt} to control LEDs')
    start_time_lapse(dt, tmax, out_path, capt=capt, exposures=exposures, save_thumbnail=True)
