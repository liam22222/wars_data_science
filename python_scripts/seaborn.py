import seaborn as sns
from matplotlib import pyplot as plt


#This def does pairploting for all columns in columns.
def MultiGraph(df, columns):
    sns.pairplot(df[columns])
    plt.show()