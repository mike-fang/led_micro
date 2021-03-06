import RPi.GPIO as GPIO
import time
import argparse

class Stepper:
    def __init__(self, pins=[11, 13, 15], pulse_time=0.005, PPR=800, pitch_mm=1):
        GPIO.cleanup()
        self.PUL, self.DIR, self.ENA = pins
        self.pulse_time=pulse_time
        self.PPR = PPR
        self.pitch_mm = pitch_mm
        
        GPIO.setmode(GPIO.BOARD)
        for _ in range(1):
            for pin in pins:
                GPIO.setup(pin, GPIO.OUT)
                #GPIO.output(pin, 0)
        self.sum_steps = 0
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
        curr_pos = self.read_pos() + pm * n_steps
        with open('./stepper_pos', 'w') as f:
            f.write(str(curr_pos))
        self.reset()
    def zero_pos(self):
        with open('./stepper_pos', 'w') as f:
            f.write(str(0.))
    def read_pos(self):
        with open('./stepper_pos', 'r') as f:
            pos = float(f.read())
        return pos
    def goto(self, x):
        dx = x - self.read_pos()
        dir_ = 'l' if dx < 0 else 'r'
        self.pulse_steps(int(abs(dx)), dir_) 
    def move(self, x, units='mm'):
        assert units in ['mm', 'um']
        if units == 'mm':
            x *= 1000
        steps = abs(int(x/1.25))
        direction = 'r' if x > 0 else 'l'
        self.pulse_steps(steps, direction=direction)
    def reset(self):
        GPIO.output(15, 0)
    

def cleanup():
    GPIO.output(15, 0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', help='Move left L steps')
    parser.add_argument('-r', help='Move right R steps')
    parser.add_argument('-g', help='Goto G')
    parser.add_argument('-w', help='Where', action='store_true')
    args = parser.parse_args()
    print(args)

    try:
        stepper = Stepper(pulse_time=0.005)
        if args.w:
            print(stepper.read_pos())
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
