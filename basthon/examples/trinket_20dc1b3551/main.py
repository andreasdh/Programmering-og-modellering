import numpy as np

def halveringsmetoden(f, a, b, tol=1E-8):
  m = (a+b)/2 
  while abs(f(m)) >= tol:
    if f(a)*f(m) < 0:
        b = m
    elif f(b)*f(m) < 0:
        a = m
    m = (a+b)/2
  return m

def c1(t):
    return np.exp(-t) + t + 5

def c2(t):
    return np.log(0.006*t + 1) + t**0.3 + 10

def c(t):
    return c1(t) - c2(t)
    
t = halveringsmetoden(c,1,100)
kons = c1(t)
print("Konsentrasjonen var", round(kons,2), "mol/L for begge reaksjoner etter", round(t,2), "sekunder")