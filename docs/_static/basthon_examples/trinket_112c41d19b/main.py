a = 1   # første verdi i tallfølgen
n = 3 # n-te ledd i tallfølgen

for i in range(1, n):
  a = a + 2**i

print("Tall nummer", n, "i følgen er:", a)