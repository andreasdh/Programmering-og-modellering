from pylab import *

# Definerer genotyper som strenger av to bokstaver
genotype_mor = "bb" 
genotype_far = "Bb"

allel1 = randint(0,2) # Trekker et tilfeldig tall mellom 0 og 1
allel2 = randint(0,2) # Trekker et nytt tilfeldig tall

# Velger ut enten første eller siste bokstav/allel i hver genotype
genotype = genotype_mor[allel1] + genotype_far[allel2]

if genotype == "bb":
  fenotype = "blå øyne"
# Fyll ut resten av vilkåret
# ...

print("Du får genotypen:", genotype, "Dette gir fenotypen:", fenotype)