from pyFiles.BaseClass import BaseClass
from pyFiles.Simulation import Simulation

class ExploratoryDataAnalysis(BaseClass,Simulation):

    def __init__(self, *args, **kwargs):
        pass
     
    def hist_plot(self, *args, **kwargs):
        ax = self.sample_.hist(columns='survive') #Using the dataFrame that has the results from Sim for all the treatments
        ax.set_xlabel("Number of Occurences")
        ax.set_ylabel("Probability of Three Star Orbit Survive")

    def box_plot(self, *args, **kwargs):
        boxplot = self.sample_.boxplot(column=['survive']

if __name__ == "__main__":
    explore = ExploratoryDataAnalysis()
    explore.hist_plot()
    explore.box_plot()
