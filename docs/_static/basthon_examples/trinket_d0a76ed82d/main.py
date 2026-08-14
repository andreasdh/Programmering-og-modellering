from pylab import *

plante1_y = ["Y", "y"]
plante1_r = ["R", "r"]
plante2_y = ["Y", "y"]
plante2_r = ["R", "r"]
grønne_rynkete = 0
N = 10000
frekvens = []
avkom = []

for antall_avkom in range(1,N+1):
    # Trekk et tilfeldig allel fra alle gener
    genotype = # regn ut genotypen
    if genotype in ["yyrr", "yryr", "yrry", "ryyr", "rryy", "ryry"]: # Hvis genotypen er noen av disse
        # fyll inn her
    frekvens.append(grønne_rynkete/antall_avkom)
    avkom.append(antall_avkom)

plot(avkom, frekvens, color = "green")
xlabel("Antall avkom")
ylabel("Relativ frekvens av grønne, rynkete erter")
axhline(y = 1/16, color = "red") # Markerer linja 1/4
show()