import cv2
import matplotlib.pylab as plt
import subprocess

class ELP_Camera():
    def __init__(self, cv_chan, auto_exp=False):
        self.cap = cv2.VideoCapture(cv_chan)
        img = self.capture_img()
        self.img_shape = img.shape
        self.set_auto_exp(auto_exp)
        self.set_auto_wb(False)
        self.set_exp(75)
        self.set_wb(2000)
    def set_auto_exp(self, val):
        if val:
            val = 3
        else:
            val = 1
        subprocess.call(["uvcdynctrl", "-s", "Exposure, Auto", str(val)])
    def set_exp(self, exp):
        subprocess.call(["uvcdynctrl", "-s", "Exposure (Absolute)", str(exp)])
    def set_auto_wb(self, v):
        if v:
            v = 1
        else:
            v = 0
        subprocess.call(["uvcdynctrl", "-s", "White Balance Temperature, Auto", str(v)])
    def set(self, prop, val):
        subprocess.call(["uvcdynctrl", "-s",str(prop), str(val)])
        subprocess.call(["uvcdynctrl", "-g",str(prop)])
    def get(self, prop):
        subprocess.call(["uvcdynctrl", "-g",str(prop)])
    def set_auto_wb(self, v):
        if v:
            v = 1
        else:
            v = 0
        subprocess.call(["uvcdynctrl", "-s", "White Balance Temperature, Auto", str(v)])
    def set_wb(self, v):
        subprocess.call(["uvcdynctrl", "-s", "White Balance Temperature", str(v)])
        subprocess.call(["uvcdynctrl", "-g", "White Balance Temperature"])
    def camera_test(self, ch='all', callback=None):
        from capture_msi import init_rb, STD_EXPOSURE
        import numpy as np
        from time import time, sleep

        def show_frame():
            _, frame = self.cap.read()
            print(frame.mean())
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
    from led_controller import LED_Controller, init_rb, Stepper
    def print_sharp(img):
        #print(get_mean_log_power(img, exp=3))
        #print(grad_sharp(img))
        return
    cam = ELP_Camera(0)
    cam.set_exp(300)
    cam.set_auto_exp(False)
    rb = init_rb()
    stepper = Stepper(pulse_time=0.0005)
    led_control = LED_Controller(rb, stepper)
    led_control.switch_on(1)
    while True:
        frame = cam.capture_img()
        cv2.imshow('', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
