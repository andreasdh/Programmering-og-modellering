def f(x):				#Definerer en funksjon som vi skal integrere.
    return x**3
    
def f_analytisk(x):     #Definerer analytisk verdi for sammenlikning.
    return (1/4)*x**4

def rektangelmetoden(f, a, b, n):
    A = 0						   
    # Beregn bredden til rektanglene her
    for k in range(n):	
        # Fyll inn her
    return # Fyll inn her
  
print("Numerisk verdi:", rektangelmetoden(f, 0, 5, 1000))
print("Analytisk verdi:", f_analytisk(5)-f_analytisk(1))