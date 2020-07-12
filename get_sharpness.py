import cv2
import numpy as np
import matplotlib.pylab as plt

img = cv2.imread('./pumpkin.jpg')
img = img[:, :, [2, 1, 0]]
img = cv2.resize(img, (640, 480))

def get_power(img):
    # Convert to greyscale
    if len(img.shape) == 3:
        img = img.mean(axis=2)

    img_fft = np.fft.fft2(img)
    img_fft = np.fft.fftshift(img_fft)
    log_power = np.log(np.abs(img_fft)**2)

    H, W = img.shape
    #R = ((H/2)**2 + (W/2)**2)**.5
    R = min(H, W)/2
    polar_power = cv2.linearPolar(log_power,(W/2, H/2), R, cv2.WARP_FILL_OUTLIERS)
    rad_power = polar_power.mean(axis=0)
    return rad_power
def get_mean_log_power(img, exp=0):
    power = get_power(img)
    freqs = np.arange(len(power))
    return ((freqs**exp * power).mean() / (freqs**exp).mean())

if __name__ == '__main__':
    sharps = []
    for n in range(20):
        img = cv2.GaussianBlur(img, (3, 3), 0)
        sharps.append(get_mean_log_power(img, exp=1))
    plt.plot(sharps)
    plt.show()
