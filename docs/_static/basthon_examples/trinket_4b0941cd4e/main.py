import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn import tree
from sklearn.metrics import accuracy_score, confusion_matrix

pingvindata = pd.read_csv("penguins.txt", delimiter = ",")

kriterier = pingvindata[['bill_length_mm', 'bill_depth_mm']] # features
kategorier = pingvindata['species']                          # labels

# Velge ut data til trening og testing
treningsandel = 0.8 # Velger 80 prosent av datasettet til trening
ml_data = train_test_split(kriterier, kategorier, train_size=treningsandel, random_state=42)

treningskriterier = ml_data[0]
testkriterier = ml_data[1]
treningskategorier = ml_data[2]
testkategorier = ml_data[3]