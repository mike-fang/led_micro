import numpy as np
import h5py
import os.path
import warnings
from glob import glob
import datetime
from analyses.lab_pca import lab_pca
import cv2
import argparse
from tqdm import tqdm

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
RESULTS = os.path.join(CUR_DIR, 'results')

def dir2h5(dir_path, overwrite=False):
    h5_name = os.path.join(dir_path, 'time_lapse.h5')
    if os.path.isfile(h5_name):
        if not overwrite:
            print('Reading h5 file')
            return h5py.File(h5_name)
        else:
            print('Overwriting existing h5 file')
            os.remove(h5_name)
    else:
        print('Converting numpy files to h5')

    npy_list = glob(os.path.join(dir_path, '*.npy'))
    npy_list.sort()
    n_arrays = len(npy_list)
    H, W, C = np.load(npy_list[0]).shape

    h5_file = h5py.File(h5_name, mode='w-')
    data = h5_file.create_dataset('data', shape=(n_arrays, H, W, C), dtype='u1')
    timestamps = h5_file.create_dataset('timestamps', shape=(n_arrays,))
    data.attrs['height'] = H
    data.attrs['width'] = W
    data.attrs['n_channels'] = C

    for n, f_name in enumerate(npy_list):
        # get timestamp and datetime string
        timestamp = int(f_name.split('/')[-1].split('_')[0])
        dt_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        arr = np.load(f_name).astype('u1')
        data[n] = arr
        timestamps[n] = timestamp

    return h5_file

def tl_lab_pca(dir_path, overwrite=False):
    out_file = os.path.join(dir_path, 'time_lapse_lab_pca.mp4')
    h5_file = dir2h5(dir_path, overwrite=False)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    if os.path.isfile(out_file):
        if overwrite:
            print('Overwriting existing video')
        else:
            print('Video already exists')
            return
    vw = cv2.VideoWriter(out_file, fourcc, 5., (640, 480))
    pca = None
    print('Making video')
    for frame in tqdm(h5_file['data']):
        img, pca = lab_pca(ms_img=frame, pca=pca, q=.01, pca_args={'whiten': True})
        vw.write(img)

if __name__ == '__main__':
    warnings.filterwarnings("ignore")

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', help='Specifiy directory to load data from')
    parser.add_argument('--new', help='Choose newest directory', action='store_true')
    parser.add_argument('--all', help='Iterate over all directories', action='store_true')
    parser.add_argument('--overwrite', help='Overwrite existing video, if exists', action='store_true')
    args = parser.parse_args()

    if args.dir:
        dirs = [os.path.join('results', args.dir)]
    elif args.all:
        dirs = glob('./results/*') 
    elif args.new:
        dirs = glob('./results/*') 
        dirs.sort(key=os.path.getmtime, reverse=True)
        dirs = [dirs[0]]
    else:
        raise Exception('No directory specified')

    for dir_path in dirs:
        print(f'--------------------')
        print(f'Processing {dir_path}...')
        tl_lab_pca(dir_path, overwrite=args.overwrite)
