import matplotlib.pyplot as plt 

tid_slutt = 2100  # År etter 1825
tid = 1825        # Startår
a = 0.045         # Utslippsrate
u = 0.01          # Utslipp i 1825 (tonn per innbygger)
tiltak = 2015

utslipp = [u]
årstall = [tid]

while tid <= tid_slutt: 
    # Legg inn modellen og fyll inn i listene her

plt.plot(årstall, utslipp)
# Pynt plottene her
plt.show()