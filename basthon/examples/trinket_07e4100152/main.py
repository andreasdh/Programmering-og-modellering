import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("temperatur.txt", delimiter = ",")

plt.plot(data["tid"], data["temperatur"])
plt.xlabel("Tid (s)")
plt.ylabel("Temperatur")
plt.show()