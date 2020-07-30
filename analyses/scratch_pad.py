import h5py
import numpy as np
import time

H, W, C = 640, 480, 24

h5_name = 'test.h5'
h5_file = h5py.File(h5_name, mode='w')
data = h5_file.create_dataset('data', shape=(0, H, W, C), maxshape=(None, H, W, C), dtype='u1')
ts_data = h5_file.create_dataset('time_stamps', shape=(0,), maxshape=(None,))

for n in range(10):
    t0 = time.time()
    ts = round(time.time(), 2)
    N = len(data)
    H, W, C = 100, 100, 3

    data.resize((N+1, H, W, C))
    ts_data.resize((N+1,))

    frame = np.random.randint(0, 255, size=(H, W, C))
    data[N] = frame
    ts_data[N] = ts
    print(time.time() - t0)

print(h5_file['data'])
print(h5_file['time_stamps'])
