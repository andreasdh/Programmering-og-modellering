import numpy as np

kolonne1 = np.array([0,1,2,3,4,5])
kolonne2 = np.array([10, 12, 9, 9, 12, 15])

data = np.array([kolonne1,kolonne2])

print(data[1,2])
print(data[1,:])
print(data[:,0])