import matplotlib.pylab as plt
import numpy as np

def show_rgb_comp(ms_img):
    for n in range(8):
        plt.subplot(2, 4, n+1)
        img = ms_img[:, :, n*3:(n+1)*3].astype(np.uint8)
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
def show_chan_comp(ms_img):
    for n in range(24):
        plt.subplot(4, 6, n+1)
        plt.imshow(ms_img[:, :, n], cmap='Greys_r')
        plt.xticks([])
        plt.yticks([])
