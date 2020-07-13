import cv2
import matplotlib.pylab as plt

class ELP_Camera():
    def __init__(self, cv_chan, auto_exp=False):
        self.cap = cv2.VideoCapture(cv_chan)
        img = self.capture_img()
        self.img_shape = img.shape
        self.set_auto_exp(auto_exp)
    def set_auto_exp(self, val):
        if val:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        else:
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    def set_exp(self, exp):
        self.cap.set(cv2.CAP_PROP_EXPOSURE, exp)
        print('Exposure is now', self.cap.get(cv2.CAP_PROP_EXPOSURE))
    def camera_test(self, ch='all', callback=None):
        from capture_msi import init_rb, STD_EXPOSURE
        import numpy as np
        from time import time, sleep

        def show_frame():
            _, frame = self.cap.read()
            cv2.imshow('', frame)
            if callback is not None:
                callback(frame)
        rb = init_rb()
        if ch == 'all':
            for n in range(8):
                sleep(.1)
                state = np.zeros(8)
                state[n] = 1
                rb.set_state(state)
                t0 = time()
                while time() < t0 + 1:
                    show_frame()
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        else:
            state = np.zeros(8)
            state[ch - 1] = 1
            rb.set_state(state)
            while True:
                show_frame()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        state = np.zeros(8)
        rb.set_state(state)
        self.cap.release()
        cv2.destroyAllWindows()
        assert False
    def capture_img(self):
        ret, frame = self.cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

if __name__ == '__main__':
    from get_sharpness import get_mean_log_power, grad_sharp
    def print_sharp(img):
        #print(get_mean_log_power(img, exp=3))
        #print(grad_sharp(img))
        return
    cam = ELP_Camera(0)
    cam.set_exp(300)
    cam.set_auto_exp(False)
    cam.camera_test(8, callback=print_sharp)
