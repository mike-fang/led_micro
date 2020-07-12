import numpy as np
import matplotlib.pylab as plt
from scipy import optimize
from scipy.stats import linregress

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

class GradOptim:
    def __init__(self, limits, max_step, eta, stage_control, eval_sharp, n_fit=5, max_hist=100):
        self.limits = limits
        self.max_step = max_step
        self.eta = eta
        self.stage = stage_control
        self.n_fit = n_fit
        self.eval_sharp = eval_sharp
    def init_measurements(self):
        self.z_buff = np.zeros(self.n_fit)
        self.s_buff = np.zeros(self.n_fit)
        self.z_hist = []
        self.s_hist = []
        z0 = self.stage.where_z()
        z0 -= self.n_fit / 2 * self.max_step
        for n in range(self.n_fit):
            z, s = self.move_and_eval(z0 + n*self.max_step)
            self.z_buff[n] = z
            self.s_buff[n] = s
            self.z_hist.append(z)
            self.s_hist.append(s)
    def get_slope_intercept(self):
        slope, intercept, _, _, _ = linregress(self.z_buff, self.s_buff)
        return slope, intercept
    def get_next_z(self):
        dz = self.get_slope_intercept()[0] * self.eta
        dz = min(max(dz, -1), 1) # force it to be between -1, 1
        step = self.max_step * dz
        if dz < 0:
            z = self.z_buff.min()
        else:
            z = self.z_buff.max()
        new_z = min(max(z + step, self.limits[0]), self.limits[1])
        return new_z
    def plot(self):
        slope, y0 = self.get_slope_intercept()
        z_range = np.linspace(*self.limits)
        plt.plot(self.z_buff, self.s_buff, 'ko')
        plt.plot(self.z_hist, self.s_hist, 'k.', alpha=.2)
        plt.plot(z_range, slope * z_range + y0, 'r--')
        new_z = self.get_next_z()
        new_s = (new_z - self.z_buff.mean()) * slope + self.s_buff.mean()
        print(new_z, new_s)
        plt.scatter(new_z, new_s, ec='blue', fc='none')
        plt.ylim([0, 2])
        plt.show()
    def move_and_eval(self, z):
        self.stage.move_to_z(z)
        s = self.eval_sharp()
        z = self.stage.where_z()
        return z, s
    def step(self):
        new_z = self.get_next_z()
        z, s = self.move_and_eval(new_z)
        self.z_buff[:-1] = self.z_buff[1:]
        self.z_buff[-1] = z
        self.s_buff[:-1] = self.s_buff[1:]
        self.s_buff[-1] = s
        self.z_hist.append(z)
        self.s_hist.append(s)
        return

class QuadOptim:
    def __init__(self, limits, max_step, stage_control, eval_sharp, n_init=5, n_fit=20, max_hist=100):
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
        z0 -= self.n_init / 2 * self.max_step
        start = self.n_fit - self.n_init
        for n in range(self.n_init):
            z, s = self.move_and_eval(z0 + n*self.max_step)
            self.record_zs(z, s)
    def get_next_z(self):
        sigma = np.exp(-np.arange(len(self.z_buff))**0.5)
        print(sigma)
        print(self.z_buff)
        params, _ = optimize.curve_fit(parabola, self.z_buff, self.s_buff, sigma=sigma)
        a, b, c = params
        z0 = self.stage.where_z()
        new_z = b / np.exp(a)
        new_z = min(max(new_z, min(self.z_buff) - self.max_step), max(self.z_buff) + self.max_step)
        new_z = min(max(new_z, self.limits[0]), self.limits[1])
        return new_z
    def plot(self):
        params, _ = optimize.curve_fit(parabola, self.z_buff, self.s_buff)
        z_range = np.linspace(*self.limits)
        plt.plot(self.z_buff, self.s_buff, 'ko')
        plt.plot(self.z_hist, self.s_hist, 'k.', alpha=.2)
        plt.plot(z_range, parabola(z_range, *params), 'r--')
        new_z = self.get_next_z()
        print(params)
        new_s = parabola(new_z, *params)
        plt.plot(z_range, f(z_range, sigma=0))
        plt.scatter(new_z, new_s, ec='blue', fc='none')
        plt.ylim([0, 8])
        plt.show()
    def move_and_eval(self, z):
        self.stage.move_to_z(z)
        s = self.eval_sharp()
        z = self.stage.where_z()
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
        z, s = self.move_and_eval(new_z)
        self.record_zs(z, s)
        return

shift = 0
def f(x, sigma=1e-2):
    global shift
    x = x - shift
    shift += np.random.uniform() * 1e-2
    try:
        noise = np.random.randn(len(x))
    except:
        noise = np.random.randn()
    return (x**2 - 5*x + 6) / (x**2 + 1) + noise * sigma
def parabola(x, a, b, c):
    x = np.array(x)
    return -0.5*np.exp(a)*x**2 + b*x + c

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
for _ in range(50):
    optimizer.step()
    optimizer.plot()



assert False
x_history = []
Xs = np.array([0, 0.02, 0.04, 0.06, 0.08]) *4
Xs += .0
Ys = f(Xs, 1e-2)
params, _ = optimize.curve_fit(parabola, Xs, Ys)
a, b, c = params
x_target = b / a
print(x_target)


xrange = np.arange(-1, 1, .01)
fit = parabola(xrange, *params)
real = f(xrange)
plt.plot(Xs, Ys, 'ko')
plt.plot([x_target], [f(x_target)], 'rx')
plt.plot(xrange, fit)
plt.plot(xrange, real)
plt.show()
