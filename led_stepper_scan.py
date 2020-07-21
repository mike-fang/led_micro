from capture_msi import init_rb
from stepper_control import Stepper
from elp_usb_cam import ELP_Camera
import numpy as np
import time

rb = init_rb()
led_ch = {
    'g' : 1, 
    'b' : 2,
    'w' : 5,
    'r' : 6,
    'o' : 7
}

state = np.ones(8)
rb.set_state(state)
