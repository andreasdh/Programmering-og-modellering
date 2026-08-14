import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("temperatur.txt", skiprows = 1, delimiter = ",") # Får to arrayer (kolonner) i en array

t = data[:,0] # velger ut alle (:) radverdier i den første kolonnen
T = data[:,1] # velger ut alle (:) radverdier i den andre kolonnen

plt.plot(t, T)
plt.xlabel("Tid (s)")
plt.xlabel("Temperatur ($^o$C)")
plt.show()