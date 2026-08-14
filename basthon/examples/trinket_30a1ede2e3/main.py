from scipy.optimize import root_scalar
import numpy as np

def f(x):
    return x**3 - 1
def dfdx(x):
    return 3*x**2
def df2dx2(x):
    return 6*x

# Nullpunkter
nullpunkt_halverings = root_scalar(f,method='bisect',bracket=[0,5])
nullpunkt_newton = root_scalar(f,method='newton',fprime=dfdx,x0=5)
nullpunkt_halley = root_scalar(f,method='halley',fprime=dfdx, fprime2=df2dx2,x0=5)
print("Halveringsmetoden:",nullpunkt_halverings)
print("Newtons metode:",nullpunkt_newton)
print("Halleys metode:",nullpunkt_halley)