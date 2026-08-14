import numpy as np

# Lager to vektorer [x, y, z]
v = np.array([1, 2, 2])
u = np.array([3, 4, 1])

# Komponentvise operasjoner
addisjon = u + v
subtraksjon = u - v
multiplikasjon = u*v
divisjon = u/v

skalarprodukt = np.dot(v, u)   # (prikkprodukt)
vektorprodukt = np.cross(v, u) # (kryssprodukt)