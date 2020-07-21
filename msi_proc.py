import matplotlib.pylab as plt
import numpy as np
from scipy.signal import fftconvolve
from sklearn.decomposition import PCA

def show_rgb_comp(ms_img):
    for n in range(5):
        plt.subplot(1, 5, n+1)
        img = ms_img[:, :, n*3:(n+1)*3].astype(np.uint8)
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
def show_rgb_comp(ms_img):
    for n in range(5):
        plt.subplot(2, 4, n+1)
        img = ms_img[:, :, n*3:(n+1)*3].astype(np.uint8)
        plt.imshow(img)
        plt.xticks([])
        plt.yticks([])
def show_chan_comp(ms_img):
    plt.figure(figsize=(6, 7))
    for n in range(24):
        plt.subplot(6, 4, n+1)
        plt.imshow(ms_img[:, :, n], cmap='Greys_r')
        plt.xticks([])
        plt.yticks([])
def pca_pseudo(msi, channels=None):
    pca = PCA()
    H, W, C = msi.shape
    if channels is None:
        channels = [0, 1, 2]
    msi_pca = pca.fit_transform(msi.reshape((-1, C))).reshape(H, W, C)
    print(channels)
    msi_pca3 = msi_pca[:, :, channels] * -1
    msi_pca3 -= msi_pca3.min()
    msi_pca3 /= msi_pca3.max()
    return msi_pca3

if __name__ == '__main__':
    msi = np.load('./results/1593486265_59.npy')
    msi_pca3 = pca_pseudo(msi, channels=[0, 3, 4])

    msi_pca3 = 1-msi_pca3
    plt.imshow(msi_pca3, cmap='Greys_r')
    plt.xticks([])
    plt.yticks([])
    plt.tight_layout()
    plt.show()
    #plt.savefig('./figures/pseduo.png')
