from pylab import *

genotype_mor = ["B", "b"]
genotype_far = ["B", "b"]
blaa = 0
N = 100

for i in range(N):    
  allel_mor = choice(genotype_mor)    
  allel_far = choice(genotype_far)    
  genotype = allel_mor + allel_far
  if genotype == "bb":        
    blaa = blaa + 1

print("Sannsynligheten for å få blå øyne er:", blaa/N)
