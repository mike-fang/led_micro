import numpy as np
import h5py
import os.path
from glob import glob
import datetime
import matplotlib.pylab as plt
from lab_pca import lab_pca
import cv2


exp_name = 'stepper_bug_grow'
h5_file = h5py.File(f'./{exp_name}.h5')
frame = h5_file['tl_imgs'][0]
for n in range(5):
    img = frame[:, :, n*3:(n+1)*3].mean(2)**1
    plt.imshow(img, cmap='Greys_r')
    plt.show()
