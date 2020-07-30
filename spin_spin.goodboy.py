import RPi.GPIO as GPIO
import time
import argparse
import json

class Stepper:
    def __init__(self, config_file, pulse_time=0.0001):
        self.load_config(config_file)
        GPIO.cleanup()
        self.pulse_time=pulse_time
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            #GPIO.output(pin, 0)
        self.sum_steps = 0
        self.curr_dir = 0
    def __enter__(self):
        self.engage()
        return self
    
    def __exit__(self, type, value, tb):
        time.sleep(.5)
        self.disengage()
        
    def load_config(self, cf):
        self.config_file = cf
        with open(cf, 'r') as f:
            self.config = json.load(f)
        self.pins = self.config['pins']
        self.PPR = self.config['PPR']
        self.PUL, self.DIR, self.ENA = self.pins
    def set_dir(self, direction):
        GPIO.output(self.DIR, direction)
        self.curr_dir = direction
    def pulse(self):
        GPIO.output(self.PUL, 1)
        time.sleep(self.pulse_time)
        GPIO.output(self.PUL, 0)
        time.sleep(self.pulse_time)
    def pulse_steps(self, n_steps, direction='l', disengage=True):
        assert n_steps > 0
        if direction in ['r', 'R', 'right']:
            direction = 0
        elif direction in ['l', 'L', 'left']:
            direction = 1
        self.set_dir(direction)
        for _ in range(n_steps):
            GPIO.output(self.DIR, direction)
            GPIO.output(self.ENA, 1)
            GPIO.output(self.PUL, 1)
            time.sleep(self.pulse_time)
            GPIO.output(self.PUL, 0)
            time.sleep(self.pulse_time)
            self.pulse()

        # accum steps
        pm = -1 if direction == 1 else +1
        curr_pos = (self.read_pos() + pm * n_steps) % self.PPR
        self.set_pos(curr_pos)
        if disengage:
            self.disengage()
    def zero_pos(self):
        with open('./stepper_pos', 'w') as f:
            f.write(str(0.))
    def set_pos(self, x):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        self.config['pos'] = x
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
    def read_pos(self):
        return self.config['pos']
    def goto(self, x):
        dx = (x - self.read_pos()) % self.PPR
        if dx > self.PPR/2:
            pass
            #dx -= self.PPR
        dir_ = 'l' if dx < 0 else 'r'
        self.pulse_steps(int(abs(dx)), dir_) 
    def goto_filter(self, f):
        if isinstance(f, int):
            positions = []
            for k, p in self.config['filters'].items():
                positions.append(p)
            pos = positions[f]
        else:
            pos = self.config['filters'][f]
        self.goto(pos)
    def move(self, x, units='mm'):
        assert units in ['mm', 'um']
        if units == 'mm':
            x *= 1000
        steps = abs(int(x/1.25))
        direction = 'r' if x > 0 else 'l'
        self.pulse_steps(steps, direction=direction)
    def engage(self):
        GPIO.output(self.ENA, 1)
    def disengage(self, wait=0):
        time.sleep(wait)
        GPIO.output(self.ENA, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', help='Move left L steps')
    parser.add_argument('-r', help='Move right R steps')
    parser.add_argument('-g', help='Go to step position G')
    parser.add_argument('-f', help='Go to filter number f')
    parser.add_argument('-w', help='Where', action='store_true')
    parser.add_argument('-t', help='Pulse Time', default='0.0001')
    parser.add_argument('--loop', help='Loop through filters L times', default='1')
    args = parser.parse_args()
    try:
        stepper = Stepper(config_file='spinspin_config.json', pulse_time=float(args.t))
        if args.w:
            print(f'Welcome to {stepper.read_pos()}, please take a seat and have some covfefe')
        if args.l:
            dir_ = 'l'
            steps = int(args.l)
            stepper.pulse_steps(steps, dir_)
            if args.r or args.g:
                raise Exception('left or right or goto? make up your mind yo!')
        elif args.r:
            dir_ = 'r'
            steps = int(args.r)
            stepper.pulse_steps(steps, dir_)
            if args.l or args.g:
                raise Exception('left or right or goto? make up your mind yo!')
        elif args.g:
            stepper.goto(int(args.g))
        elif args.f:
            stepper.goto_filter(int(args.f))
        elif args.loop:
            for _ in range(int(args.loop)):
                stepper.goto_filter(0)
#                 stepper.goto_filter(1)
#                 stepper.goto_filter(2)
#                 stepper.goto_filter(3)
        else:
            stepper.engage()
            for _ in range(20):
                stepper.pulse_steps(200, 'l', disengage=False)
                stepper.pulse_steps(200, 'r', disengage=False)
    except Exception as e:
        print(e)
        stepper.disengage()
    else:
        stepper.disengage()