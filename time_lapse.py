import cv2
import numpy as np
from datetime import datetime
from capture_msi import capture_ms_img, init_rb, get_exposures
import os, time
from elp_usb_cam import ELP_Camera
import matplotlib.pylab as plt
from msi_proc import *
import argparse


def start_time_lapse(dt, tmax, out_path, exposures=None, save_thumbnail=False):
	if not os.path.isdir(out_path):
		os.makedirs(out_path)
	cam = ELP_Camera(0)
	t0 = time.time()
	rb = init_rb()
	while time.time() - t0 < tmax:
		start_time = time.time()
		ms_img = capture_ms_img(cam, rb, exposures=exposures, pause=.5)
		time_stamp = f'{time.time():.2f}'.replace('.', '_')
		np.save(os.path.join(out_path, f'{time_stamp}.npy'), ms_img)
		if save_thumbnail:
			plt.figure()
			show_rgb_comp(ms_img)
			plt.savefig(os.path.join(out_path, f'{time_stamp}_tn.png'))
			cv2.imwrite(os.path.join(out_path, f'{time_stamp}_white.png'), ms_img[:, :, -1])
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

	args = parser.parse_args()

	CUR_DIR = os.path.abspath(os.path.dirname(__file__))
	out_path = os.path.join('results', args.dir[0])

	dt = float(args.dt) * 60
	tmax = float(args.tmax) * 60

	exposures = np.load('./exposures.npy')
	print('Starting time-lapse capture...')
	print(f'  Time between capture {dt / 60:.2f} mins')
	print(f'  Total time of cpature {tmax / 60:.2f} mins')
	print(f'  Output saved to {out_path}')
	start_time_lapse(dt, tmax, out_path, exposures=exposures, save_thumbnail=True)
