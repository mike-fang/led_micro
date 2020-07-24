import RPi.GPIO as GPIO
import time
import argparse
import json

class Stepper:
    def __init__(self, config_file, pulse_time=0.005):
        self.load_config(config_file)
        GPIO.cleanup()
        self.pulse_time=pulse_time
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            #GPIO.output(pin, 0)
        self.sum_steps = 0
    def load_config(self, cf):
        self.config_file = cf
        with open(cf, 'r') as f:
            self.config = json.load(f)
        self.pins = self.config['pins']
        self.PPR = self.config['PPR']
        self.PUL, self.DIR, self.ENA = self.pins
    def pulse_steps(self, n_steps, direction='l'):
        if direction in ['r', 'R', 'right']:
            direction = 0
        elif direction in ['l', 'L', 'left']:
            direction = 1
        if n_steps < 0:
            direction = 0
            n_steps = -n_steps
        for _ in range(n_steps):
            GPIO.output(self.DIR, direction)
            GPIO.output(self.ENA, 1)
            GPIO.output(self.PUL, 1)
            time.sleep(self.pulse_time)
            GPIO.output(self.PUL, 0)
            time.sleep(self.pulse_time)
        # accum steps
        pm = -1 if direction == 1 else +1
        curr_pos = (self.read_pos() + pm * n_steps) % self.PPR
        self.set_pos(curr_pos)
        self.reset()
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
            dx -= self.PPR
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
    def reset(self):
        GPIO.output(self.ENA, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', help='Move left L steps')
    parser.add_argument('-r', help='Move right R steps')
    parser.add_argument('-g', help='Goto G')
    parser.add_argument('-w', help='Where', action='store_true')
    args = parser.parse_args()
    try:
        stepper = Stepper(config_file='spinspin_config.json', pulse_time=0.0005)
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
    except Exception as e:
        print(e)
        stepper.reset()
    else:
        stepper.reset()