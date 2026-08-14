x0 = -10   # Startpunkt
dx = 1E-5  # Forskjellen mellom x-verdier

# Definerer funksjonen
def f(x):
    return 2*x + 2

x1 = x0    # Velger første x-verdi
x2 = x1+dx # Velger andre x-verdi
while f(x1)*f(x2) > 0:
    # Fyll ut kode her
    
x = (x2+x1)/2
print("x =", x)