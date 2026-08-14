import pandas as pd

pingvindata = pd.read_csv("penguins.txt", delimiter = ",")

snitt = pingvindata["body_mass_g"].mean()                           # gjennomsnitt
median = pingvindata["body_mass_g"].median()                        # median (midtre verdi)
standardavvik = pingvindata["body_mass_g"].std()                    # estimert standardavvik
kvartiler = pingvindata["body_mass_g"].quantile([0.25, 0.50, 0.75]) # kvartiler/persentiler (når det ikker er 25, 50 eller 75, kaller vi det persentiler)
minimum = pingvindata["body_mass_g"].min()    
maksimum = pingvindata["body_mass_g"].max()

print(kvartiler)