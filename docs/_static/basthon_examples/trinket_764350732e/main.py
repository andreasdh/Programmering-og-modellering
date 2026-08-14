import matplotlib.pyplot as plt

fil = open("temperatur.txt", 'r')	# Åpner dokumentet i lesemodus (r = read)
fil.readline()                    # Hopper over første linje (overskriften med tekst)
t = []						                # Lager tom liste med tid
T = []					                 	# Lager tom liste med temperatur

for rad in fil:				            # For hver rad i fila...
  data = rad.split(",")		      # lages ei liste kalt data med de to elementene i raden, som identifiseres med komma som separator
  t.append(float(data[0]))		  # Legger til element 0 i lista til t
  T.append(float(data[1]))		  # Legger til element 1 i lista til T
fil.close()

plt.plot(t, T)
plt.xlabel("Tid (s)")
plt.xlabel("Temperatur ($^o$C)")
plt.show()