import numpy as np
import h5py
import os.path
from glob import glob
import datetime
import matplotlib.pylab as plt
from lab_pca import lab_pca
import cv2

def dir2h5(exp_name, overwrite=False):
    CUR_DIR = os.path.abspath(os.path.curdir)
    dir = os.path.join(CUR_DIR, exp_name)

    npy_list = glob(os.path.join(dir, '*.npy'))
    npy_list.sort()
    n_arrays = len(npy_list)

    H, W, C = np.load(npy_list[0]).shape

    h5_name = os.path.join(CUR_DIR, f'{exp_name}.h5')
    if os.path.isfile(h5_name):
        if not overwrite:
            raise Exception(f'File {h5_name} already exists.')
        os.remove(h5_name)
    h5_file = h5py.File(h5_name, mode='w-')
    data = h5_file.create_dataset('tl_imgs', shape=(n_arrays, H, W, C), dtype='u1')
    data.attrs['height'] = H
    data.attrs['width'] = W
    data.attrs['n_channels'] = C

    for n, f_name in enumerate(npy_list):
        # get timestamp and datetime string
        timestamp = int(f_name.split('/')[-1].split('_')[0])
        dt_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        arr = np.load(f_name).astype('u1')
        data[n] = arr

    return h5_file

if __name__ == '__main__':
    exp_name = 'ecoliK12withringtiptrack2'
    try:
        h5_file = dir2h5(exp_name, overwrite=True)
    except:
        h5_file = h5py.File(f'./{exp_name}.h5')
        assert False

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(f'{exp_name}.mp4', fourcc, 5., (640, 480))
    if False:
        pca = None
        frame = h5_file['tl_imgs'][0]
        for n in range(5):
            img = frame[:, :, n*3:(n+1)*3].mean(2)**2

            #vw.write(frame[:, :, n*3:(n+1)*3].mean(2)**2, cmap='Greys_r')

        assert False
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(f'{exp_name}.mp4', fourcc, 5., (640, 480))
    pca = None
    for frame in h5_file['tl_imgs']:
        img, pca = lab_pca(ms_img=frame, pca=pca, q=.01, pca_args={'whiten': True})
        vw.write(img)
