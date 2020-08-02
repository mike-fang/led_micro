import cv2
import numpy as np
from datetime import datetime
import h5py
import os, time
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *
import argparse

TEST = False
if not TEST:
    from capture_msi import init_rb
    from capture_msi import capture_ms_img as relay_capture
    from capture_msi_stepper import capture_ms_img as stepper_capture
    from capture_msi_spin import capture_ms_img as spin_capture
    from stepper_control import Stepper
    from spin_spin import Stepper as SpinSpin

class TimeLapse:
    def __init__(self, dt, tmax, out_path, ctrl='spinspin', exposures=None, save_tn=True):
        self.dt = dt
        self.tmax = tmax
        self.ctrl = ctrl
        self.exposures = exposures
        self.save_tn = save_tn
        self.init_dirs(out_path)
        self.init_ctrl()
        self.n_frames = int(np.ceil(tmax/dt))
        self.frame_n = 0
    def get_th(self):
        if self.ctrl == 'test':
            return np.random.random(size=2)
        else:
            from temp_hum import get_th
            return get_th()
    def init_dirs(self, out_path):
        self.out_path = out_path
        self.tn_path = os.path.join(out_path, 'thumbnails')
        self.temp_path = os.path.join(out_path, 'temp_hum.txt')
        if not os.path.isdir(self.tn_path):
            os.makedirs(self.tn_path)
        with open(self.temp_path, 'w') as f:
            f.write('time \t temp \t hum\n')
    def get_msi(self):
        cam, rb, stepper = self.cam, self.rb, self.stepper
        if self.ctrl == 'stepper':
            self.n_leds = 5
            ms_img = stepper_capture(cam, rb, stepper, n_leds=5, exposures=exposures)
        elif ctrl == 'spinspin':
            self.n_leds = 4
            ms_img = spin_capture(cam, rb, stepper, n_leds=4, exposures=exposures, pause=1)
        elif ctrl == 'relay':
            self.n_leds = 8
            ms_img = relay_capture(cam, rb, n_leds=8, exposures=exposures)
        elif self.ctrl == 'test':
            self.n_leds = 8
            ms_img = np.random.randint(0, 255, size=(640, 480, 3 * self.n_leds))
        return ms_img
    def init_ctrl(self):
        if self.ctrl == 'test':
            cam = None
            rb = None
            stepper = None
        else:
            print('Init. Cam..')
            cam = ELP_Camera(0)
            print('Init. Relay..')
            rb = init_rb()
            print('Init. Stepper..')
            if self.ctrl == 'stepper':
                stepper = Stepper(pulse_time=0.00050)
            elif self.ctrl == 'spinspin':
                stepper = SpinSpin(config_file='spinspin_config.json', pulse_time=0.0005)
        self.cam = cam
        self.rb = rb
        self.stepper = stepper
    def write_h5(self, msi, ts, init=False):
        print(self.n_frames)
        H, W, C = msi.shape
        print(H, W, C)
        if init:
            self.h5_path = os.path.join(self.out_path, 'time_lapse.h5')
            self.h5_file = h5py.File(self.h5_path, mode='w')
            self.h5_data = self.h5_file.create_dataset('data', shape=(self.n_frames, H, W, C), dtype='u1')
            self.h5_ts = self.h5_file.create_dataset('time_stamps', shape=(self.n_frames,), maxshape=(None,))
            self.h5_temp = self.h5_file.create_dataset('temp', shape=(self.n_frames,), maxshape=(None,))
            self.h5_hum = self.h5_file.create_dataset('hum', shape=(self.n_frames,), maxshape=(None,))
        
        self.h5_data[self.frame_n] = msi
        self.h5_ts[self.frame_n] = ts
    def write_tn(self, msi, ts):
        time_stamp = f'{ts:.2f}'.replace('.', '_')
        plt.figure()
        show_rgb_comp(msi, n_leds=self.n_leds)
        plt.savefig(os.path.join(self.tn_path, f'{time_stamp}_tn.png'))
        cv2.imwrite(os.path.join(self.tn_path, f'{time_stamp}_white.png'), msi.mean(axis=2))
        plt.cla()
        plt.clf()
        plt.close()
    def write_temp_hum(self, ts):
        time_stamp = f'{ts:.2f}'.replace('.', '_')
        temp, hum = self.get_th()
        with open(self.temp_path, 'a') as f:
            f.write(f'{time_stamp} \t {temp} \t {hum}\n')

        self.h5_temp[self.frame_n] = temp
        self.h5_hum[self.frame_n] = ts
    def start(self):
        if not os.path.isdir(out_path):
            os.makedirs(out_path)
        cam, rb, stepper = self.cam, self.rb, self.stepper
        t0 = time.time()
        init = True
        while time.time() - t0 < tmax:
            start_time = time.time()
            print('getting_msi')
            ms_img = self.get_msi()
            print('Writing h5')
            self.write_h5(ms_img, round(start_time, 2), init)
            init = False
            if self.save_tn:
                print('Writing tn')
                self.write_tn(ms_img, start_time)
            print('Writing th')
            self.write_temp_hum(start_time)
            end_time = time.time()
            time_elapsed = end_time - start_time
            sleep_time = dt - time_elapsed
            self.frame_n += 1
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
    parser.add_argument('--ctrl', help='Controller ("relay", "stepper", or "spinspin")')
    parser.add_argument('--exp', help='Exposure', default='2000')

    args = parser.parse_args()

    CUR_DIR = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join('results', args.dir[0])

    dt = float(args.dt) * 60
    tmax = float(args.tmax) * 60
    if not args.ctrl in ['relay', 'stepper', 'spinspin', 'test']:
        raise Exception('Controller needs to be "relay", "stepper" or "spinspin", yo!')
    ctrl = args.ctrl
    exposures = float(args.exp)
    print('Starting time-lapse capture...')
    print(f'  Time between capture {dt / 60:.2f} mins')
    print(f'  Total time of cpature {tmax / 60:.2f} mins')
    print(f'  Output saved to {out_path}')
    print(f'  Using {ctrl} to control LEDs')
    print(f'  Exposure set at {exposures:.2f}')
    tl = TimeLapse(dt, tmax, out_path, ctrl=ctrl, exposures=exposures, save_tn=True)
    tl.start()
    #start_time_lapse(dt, tmax, out_path, capt=capt, exposures=exposures, save_thumbnail=True)
