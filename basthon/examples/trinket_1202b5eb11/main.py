from pylab import *

antall_kast = 10
antall_mynt = 0
antall_kron = 0

for i in range(antall_kast):
    kast = randint(0,2) # Genererer et tilfeldig tall mellom 0 og 1
    if kast == 0:
        antall_mynt = antall_mynt + 1
    else:
        antall_kron = antall_kron + 1

print("Relativ frekvens av mynt:", antall_mynt/antall_kast)

