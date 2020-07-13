import numpy as np
import matplotlib.pylab as plt
from scipy import optimize
from scipy.stats import linregress
from time import sleep

class MockStage:
    def __init__(self, z_init, limits=None):
        self.z = z_init
        self.limits = limits
    def where_z(self):
        return self.z
    def move_to_z(self, z):
        if self.limits is not None:
            z = min(max(z, self.limits[0]), self.limits[1])
        self.z = z
    def move_z(self, dz):
        new_z = self.z + dz
        self.move_to_z(new_z)

class QuadOptim:
    def __init__(self, limits, max_step, stage_control, eval_sharp, n_init=5, n_fit=10, max_hist=100):
        self.limits = limits
        self.max_step = max_step
        self.stage = stage_control
        self.n_fit = n_fit
        self.n_init = n_init
        self.eval_sharp = eval_sharp
        self.max_hist = max_hist
    def init_measurements(self):
        self.z_buff = []
        self.s_buff = []
        self.z_hist = []
        self.s_hist = []
        z0 = self.stage.where_z()
        z_start = z0 - self.n_init / 2 * self.max_step
        start = self.n_fit - self.n_init
        for n in range(self.n_init):
            z = z_start + n*self.max_step
            self.move_and_eval(z)
        self.move_and_eval(z0)
    def parabola(self, x, a, b, c):
        return -0.5*np.exp(a)*x**2 + b*x + c
    def get_next_z(self):
        sigma = np.exp(-np.arange(len(self.z_buff))**0.5)
        sigma=None
        params, _ = optimize.curve_fit(self.parabola, self.z_buff, self.s_buff, sigma=sigma)
        a, b, c = params
        z0 = self.stage.where_z()
        new_z = b / np.exp(a)
        #new_z = min(max(new_z, min(self.z_buff) - self.max_step), max(self.z_buff) + self.max_step)
        new_z = min(max(new_z, z0 - self.max_step), z0 + self.max_step)
        return new_z
    def plot(self):
        params, _ = optimize.curve_fit(self.parabola, self.z_buff, self.s_buff)
        z_range = np.linspace(*self.limits)
        plt.plot(self.z_buff, self.s_buff, 'ko')
        plt.plot(self.z_hist, self.s_hist, 'k.', alpha=.2)
        plt.plot(z_range, self.parabola(z_range, *params), 'r--')
        new_z = self.get_next_z()
        new_s = self.parabola(new_z, *params)
        plt.scatter(new_z, new_s, ec='blue', fc='none')
        plt.ylim([min(self.s_buff), max(self.s_buff)])
        #plt.xlim([min(self.z_buff), max(self.z_buff)])
        plt.show()
    def move_and_eval(self, z, record=True):
        z = min(max(z, self.limits[0]), self.limits[1])
        z = float(z)
        print(type(z))
        print(f'Moving to z={z:.2f}')
        self.stage.goto_z(z)
        sleep(1) 
        s = self.eval_sharp()
        z = self.stage.where_z()
        print(f'Now at z={z:.2f}')
        print(f'')
        if record:
            self.record_zs(z, s)
        return z, s
    def record_zs(self, z, s):
        self.z_buff.append(z)
        self.s_buff.append(s)
        while len(self.z_buff) > self.n_fit:
            self.z_buff.pop(0)
        while len(self.s_buff) > self.n_fit:
            self.s_buff.pop(0)
        self.z_hist.append(z)
        self.s_hist.append(s)
        while len(self.z_hist) > self.max_hist:
            self.z_hist.pop(0)
        while len(self.s_hist) > self.max_hist:
            self.s_hist.pop(0)
    def step(self):
        new_z = self.get_next_z()
        self.move_and_eval(new_z)
        return

class GradOptim(QuadOptim):
    def __init__(self, limits, max_step, stage_control, eval_sharp, n_init=5, n_fit=10, max_hist=100, eta=.1):
        super().__init__(limits, max_step, stage_control, eval_sharp, n_init, n_fit, max_hist)
        self.eta = eta
    def get_slope_intercept(self):
        return linregress(self.z_buff, self.s_buff)[:2]
    def get_next_z(self):
        m, b = self.get_slope_intercept()
        dz = min(max(m*self.eta, -self.max_step), self.max_step)
        if dz > 0:
            z0 = max(self.z_buff)
        else:
            z0 = min(self.z_buff)
        z0 = self.stage.where_z()
        new_z = z0 + dz
        return new_z

if __name__ == '__main__':
    
    limits = [-3, 3]
    stage = MockStage(1, limits=limits)
    def eval_sharp():
        x = stage.where_z()
        return f(x, 1e-2)

    n_fit = 5
    z_buff = np.zeros(n_fit)
    s_buff = np.zeros(n_fit)
    max_step = 2
    #optimizer = GradOptim(limits=limits, max_step=max_step, eta=5, stage_control=stage, eval_sharp=eval_sharp)
    optimizer = QuadOptim(limits=limits, max_step=max_step, stage_control=stage, eval_sharp=eval_sharp)
    optimizer.init_measurements()
    for _ in range(10):
        optimizer.step()
        optimizer.plot()
