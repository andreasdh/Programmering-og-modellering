startkapital = 5000
penger = startkapital
år = 0
rente = 0.05

while penger < startkapital*2:
  penger = penger*rente
  år = år + 1
  
print("Det tar", år, "år å doble beløpet.")