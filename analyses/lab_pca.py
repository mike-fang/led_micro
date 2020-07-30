import numpy as np
import cv2
import matplotlib.pylab as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
from sklearn.decomposition import PCA
from skimage.color import lab2rgb

def get_pca(ms_img, pca=None, n_comps=3, pca_args={}):
    """
    Args:
        ms_img: A (H, W, C) representing a C-channel multispectral image
        n_comps: The number of components to be returned by PCA
    Returns:
        bases: The projection bases
        pca_img: A (H, W, n_comp) array representing a lower dimensional image
    """
            
    H, W, C = ms_img.shape

    #Reshape to (N, C) where N = H*W is the number of pixels
    flat_img = ms_img.reshape((-1, C))
    if pca is None:
        pca = PCA(n_components=3, **pca_args)
        flat_pca_img = pca.fit_transform(flat_img)
    else:
        flat_pca_img = pca.transform(flat_img)

    #Reshape back to image with n_comps channels :(H, W, n_comps)
    pca_img = flat_pca_img.reshape((H, W, n_comps))
    bases = pca.components_.T
    return pca, bases, pca_img
def unnormed_lab2rgb(ulab, q=0):
    """
    Converts an unnormalized Lab image to RGB
    Args:
        ulab: A (H, W, 3) array representing an unnormed Lab image
        q: The fraction of extreme values to be clipped (default: q=0, i.e. no clipping)
    Returns:
        A RGB image represented by a (H, W, 3) array.
    """
    # Normalize array so that the q and (1-q) quantiles are 0 and 1 respectively
    m = np.quantile(ulab, q)
    M = np.quantile(ulab, 1-q)
    lab = (ulab - m) / (M - m)
    # Clip values to [0, 1] 
    lab[lab > 1] = 1
    lab[lab < 0] = 0
    #Scale values so that L ~ [0, 100], a ~ [-100, 100], b ~ [-100, 100]
    AB_range = 100
    lab *= np.array([[ [100, 2*AB_range, 2*AB_range] ]])
    lab -= np.array([[ [0, AB_range, AB_range] ]])
    return lab2rgb(lab)
def lab_pca(ms_img, pca=None, q=0, pca_args={}, uint8=True):
    pca, _, pca_img = get_pca(ms_img, pca=pca, pca_args=pca_args)
    img = unnormed_lab2rgb(pca_img, q=q)
    if uint8:
        img = (255 * img).astype(np.uint8)
    return img, pca
def illum_correction(ms_img, ref_img):
    pass

if __name__ == '__main__':
    path = '../results/ecoliK12withringtiptrack2/1596035298_17.npy' 
    ref_img = np.load('./ref_spinspin.npy')
    ms_img = np.load(path)
    corr_img = ms_img.astype(np.float)/ref_img
    ms_cut = ms_img[:, 320,:]
    corr_cut = corr_img[:, 320,:]
    plt.subplot(211)
    plt.plot(ms_cut)
    plt.subplot(212)
    plt.plot(corr_cut)
    plt.show()
    assert False
    img, _ = lab_pca(corr_img, q=0.05, pca_args={'whiten': True})
    plt.imshow(img)
    plt.show()
