
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import pyFiles.Functions as fun

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import ipdb

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class DataSet:

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__(self, simData, Xcols, Ycols):
        # add attriutes
        self.Xcols_ = Xcols
        self.Ycols_ = Ycols
        self.YhatCols_ = [f"{col}_hat" for col in Ycols]
        self.K_ = len(Ycols)
        self.df_ = simData.copy()
        for col in self.YhatCols_: self.df_[col] = 0

    #===========================================================================#
    # puplic methods                                                            #
    #===========================================================================#

    def update(self, Yhat):
        # if feeding in 1D row, one-hot the array first
        if len(Yhat.shape) == 1: Yhat = fun.oneHotEncodeY(Yhat, K=self.K_)
        # update Yhat
        self.df_[self.YhatCols_] = Yhat
        # update confusion matrix
        self.CM_ = fun.confusionMatrix(self.Y(), Yhat)
        # update accuracy, precision, and recall
        try:
            self.accuracy_ = fun.accuracy(self.CM_)
            self.precision_ = fun.precision(self.CM_)
            self.recall_ = fun.recall(self.CM_)
        except:
            print("OOPSIE! something went wrong.\nEntering debugger")
            ipdb.set_trace()

    def X(self):
        return self.df_[self.Xcols_].values

    def Y(self):
        return self.df_[self.Ycols_].values

    def Yhat(self):
        return self.df_[self.YhatCols_].values

    def y(self):
        Y = self.Y()
        return Y.argmax(axis=1)

    def yhat(self):
        Yhat = self.Yhat()
        return Yhat.argmax(axis=1)

    #===========================================================================#
    # semp-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#
