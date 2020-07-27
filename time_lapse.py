import cv2
import numpy as np
from datetime import datetime
from capture_msi import init_rb
from capture_msi import capture_ms_img as relay_capture
from capture_msi_stepper import capture_ms_img as stepper_capture
from capture_msi_spin import capture_ms_img as spin_capture
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
    if capt == 'spinspin':
        stepper = SpinSpin(config_file='spinspin_config.json', pulse_time=0.0005)
    while time.time() - t0 < tmax:
        start_time = time.time()
        if capt == 'stepper':
            n_leds = 5
            ms_img = stepper_capture(cam, rb, stepper, n_leds=n_leds, exposures=exposures)
        if capt == 'spinspin':
            n_leds = 4
            ms_img = spin_capture(cam, rb, stepper, n_leds=n_leds, exposures=exposures, pause=1)
        elif capt == 'relay':
            n_leds = 8
            ms_img = relay_capture(cam, rb, n_leds=8, exposures=exposures)
        time_stamp = f'{time.time():.2f}'.replace('.', '_')
        np.save(os.path.join(out_path, f'{time_stamp}.npy'), ms_img)
        if save_thumbnail:
            plt.figure()
            show_rgb_comp(ms_img, n_leds=n_leds)
            plt.savefig(os.path.join(out_path, f'{time_stamp}_tn.png'))
            cv2.imwrite(os.path.join(out_path, f'{time_stamp}_white.png'), ms_img[:, :, -1])
            plt.cla()
            plt.clf()
            plt.close()
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
    parser.add_argument('--ctrl', help='Controller ("relay", "stepper", or "spinspin")')
    parser.add_argument('--spinspin', help='Using spin spin motor', action='store_true')

    args = parser.parse_args()

    CUR_DIR = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join('results', args.dir[0])

    dt = float(args.dt) * 60
    tmax = float(args.tmax) * 60
    if not args.ctrl in ['relay', 'stepper', 'spinspin']:
        raise Exception('Controller needs to be "relay", "stepper" or "spinspin", yo!')
    capt = args.ctrl
    #exposures = np.load('./exposures.npy')
    exposures = 150
    print('Starting time-lapse capture...')
    print(f'  Time between capture {dt / 60:.2f} mins')
    print(f'  Total time of cpature {tmax / 60:.2f} mins')
    print(f'  Output saved to {out_path}')
    print(f'  Using {capt} to control LEDs')
    start_time_lapse(dt, tmax, out_path, capt=capt, exposures=exposures, save_thumbnail=True)
