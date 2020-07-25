from elp_usb_cam import *
import time
from get_sharpness import get_mean_log_power, grad_sharp
import numpy as np
from led_controller import LED_Controller, init_rb, Stepper
def print_sharp(img):
    #print(get_mean_log_power(img, exp=3))
    #print(grad_sharp(img))
    return
cam = ELP_Camera(0)
cam.set_auto_exp(False)
cam.set_auto_wb(False)
cam.set_exp(50)
cam.set_wb(2000)
cam.get("White Balance Temperature")
rb = init_rb()
state = np.zeros(8)
state[4] = 1
rb.set_state(state)
#stepper = Stepper(pulse_time=0.0005)
#led_control = LED_Controller(rb, stepper)
#led_control.switch_on(4)
while True:
    frame = cam.capture_img()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow('', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
led_control.all_off()
