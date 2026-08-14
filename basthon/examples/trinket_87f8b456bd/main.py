import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-2, 3, 10)

def f(x):
    return x**2 - 2*x

def g(x):
    return np.sin(x)

def h(x):
    return - x + 6

y1 = f(x)
y2 = g(x)
y3 = h(x)

plt.plot(x,y1,color='lawngreen',label='f(x)', marker='^')
plt.plot(x,y2,color='maroon',label='g(x)', marker='o')
plt.plot(x,y3,color='deepskyblue',label='h(x)', marker='s')
plt.legend() # Viser merkelappene
plt.xlabel('x')
plt.ylabel('y')
plt.axhline(y=0,color='black') # Tegner x-akse
plt.axvline(x=0,color='black') # Tegner y-akse
plt.grid()
plt.show()