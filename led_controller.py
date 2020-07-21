from ft245r import relay_ft245r
from ft245r.relay_ft245r import FT245R
from elp_usb_cam import ELP_Camera
import numpy as np
from stepper_control import Stepper

def init_rb():
    rb = FT245R()
    dev_list = rb.list_dev()

    if len(dev_list) == 0:
        print('No FT245R devices found')
        sys.exit()
        
    dev = dev_list[0]
    print('Using device with serial number ' + str(dev.serial_number))
    rb.connect(dev)

    return rb

class LED_Controller:
    led_chs = [6, 2, 1, 7, 5]
    led_pos = [8240, 15590, 22190, 31390, 36500]
    def __init__(self, rb, stepper):
        self.rb = rb
        self.stepper = stepper
    def switch_on(self, led_n):
        ch = self.led_chs[led_n]
        x = self.led_pos[led_n]
        # off
        self.all_off()
        # move
        self.stepper.goto(x)
        # on
        state = np.zeros(8)
        state[ch - 1] = 1
        self.rb.set_state(state)
    def all_off(self):
        self.rb.set_state(np.zeros(8))
    
if __name__ == '__main__':
    from time import sleep
     
    rb = init_rb()
    stepper = Stepper(pulse_time=0.00005)
    led_control = LED_Controller(rb, stepper)
    for n in range(5):
        led_control.switch_on(n)
        sleep(1)
    led_control.all_off()
