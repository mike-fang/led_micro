import h5py
import matplotlib.pylab as plt

h5file = h5py.File('./results/temp_test/time_lapse.h5')
plt.imshow(h5file['data'][0, :, :, 1])
plt.show()
