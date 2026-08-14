import numpy as np
import time

N = 1000000
a = np.linspace(0, 10, N)
b = np.linspace(1, 11, N)
c = np.zeros(N)

tid_start1 = time.time() # registrerer starttidspunkt

for i in range(N):       # løkke der vi legger sammen a og b komponentvis
  c[i] = a[i] + b[i]
  
tid_slutt1 = time.time() # registrerer slutt-tidspunkt

tid_start2 = time.time()

c = a + b                # vektorisert kode

tid_slutt2 = time.time()

print("Ikke-vektorisert:", tid_slutt1 - tid_start1, "sekunder.")
print("Vektorisert kode:", tid_slutt2 - tid_start2, "sekunder.")