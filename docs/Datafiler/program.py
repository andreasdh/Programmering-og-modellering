

import numpy as np
import matplotlib.pyplot as plt

# Leser og sorterer fildata
sept = np.loadtxt('sept.txt',skiprows=1,dtype=str)
dec = np.loadtxt('dec.txt',skiprows=1,dtype=str)

dates_sept = sept[:,0]
conc_sept = sept[:,2]
dates_dec = dec[:,0]
conc_dec = dec[:,2]

# Funksjoner for sortering, gjennomsnitt og standardavvik
def sort_year(list_dates, list_conc):
    list_year1 = []; list_year2 = []; list_year3 = []
    for i in range(len(list_dates)):
        if list_dates[i].startswith('2002'):
            list_year1.append(float(list_conc[i]))
        elif list_dates[i].startswith('2003'):
            list_year2.append(float(list_conc[i]))
        elif list_dates[i].startswith('2004'):
            list_year3.append(float(list_conc[i]))
    return list_year1, list_year2, list_year3

def gjennomsnitt(liste1,liste2,liste3):
    snitt = []
    for i in range(len(liste1)):
        verdi = (1/3)*(liste1[i] + liste2[i] + liste3[i])
        snitt.append(verdi)
    return snitt

def standardavvik(liste1,liste2,liste3,snitt):
    avvik = []
    for i in range(len(liste1)):
        verdi = np.sqrt((1/3)*((liste1[i] - snitt[i])**2 + (liste2[i] - snitt[i])**2 + (liste3[i] - snitt[i])**2))
        avvik.append(verdi)
    return avvik

# Kaller funksjoner
conc_sept_2002, conc_sept_2003, conc_sept_2004 = sort_year(dates_sept, conc_sept)
conc_dec_2002, conc_dec_2003, conc_dec_2004 = sort_year(dates_dec, conc_dec)

snitt_sept = gjennomsnitt(conc_sept_2002, conc_sept_2003, conc_sept_2004)
snitt_dec = gjennomsnitt(conc_dec_2002, conc_dec_2003, conc_dec_2004)
std_sept = standardavvik(conc_sept_2002, conc_sept_2003, conc_sept_2004, snitt_sept)
std_dec = standardavvik(conc_dec_2002, conc_dec_2003, conc_dec_2004, snitt_dec)

