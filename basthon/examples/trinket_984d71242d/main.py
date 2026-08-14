a = [1, 2, 3]
b = [4, 5, 6]
c = a + b	  	# Legger liste b til liste a (ikke matematisk!)
print(c)		

print(c[2])		# Skriver ut element 2 i liste c
del c[2]	    # Sletter element 2
print(3 in c)	# Spør om variabelen 3 fortsatt er i c

print(max(c), min(c)) # skriver ut den største og minste verdien i c