import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

iris = pd.read_csv("iris.txt")
corr = iris.corr()

sns.heatmap(corr, annot=True,)
plt.xticks(rotation=45)  
plt.show()