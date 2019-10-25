
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from pyFiles.BaseClass import BaseClass

import pyFiles.Functions as fun
import pyFiles.Input as inp

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import itertools
import numpy as np
import pandas as pd
import pdb

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class MLbase(BaseClass):

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__(self, name, *args, **kwargs):

        # construct smaller set of kwargs used for construction
        kwargs1 = {}
        if 'verbose' in kwargs: kwargs1['verbose'] = kwargs['verbose']

        # run BaseClass constructor for Simulation instance
        super().__init__(name, *args, **kwargs)

        # set hyper-parameter map only if it doesn't exist yet
        if not hasattr(self, 'parameterMap_'): self._getParameterMap(**kwargs)

        # add DataFrame sim data if not present
        if not hasattr(self, 'data_'): self._splitData()

    #===========================================================================#
    # public methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # puplic methods                                                            #
    # required by BaseClass, implemented here                                   #
    # OR                                                                        #
    # required for MLbase, child needs to implement                             #
    #===========================================================================#

    def fit(self, *args, **kwargs):
        NotImplemented

    def predict(self, *args, **kwargs):
        NotImplemented

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

    def _performanceAccuracy(self, predictions):
        NotImplemented

    def _performancePrecision(self, predictions):
        NotImplemented

    def _performanceRecall(self, predictions):
        NotImplemented

    def _splitData(self, DF):

        # load generated sim data

        # split data

        self.data_ = {
            'train': NotImplemented,
            'validate': NotImplemented,
            'test': NotImplemented,
        }

    #===========================================================================#
    # semi-protected methods                                                    #
    # required by BaseClass, implented here                                     #
    # OR                                                                        #
    # required for MLbase, child needs to implement                             #
    #===========================================================================#

    def _getParameterMap(self, *args, **kwargs):
        NotImplemented

    def _getSample(self, **kwargs):
        self.sample_ = pd.DataFrame(
            list(itertools(self.parameterMap_.values())),
            columns = self.parameterMap_.keys()
        )
        # add columns to track model performance for train, validate, test
        metricCols = []
        for metric in ['accuracy', 'recall', 'precision']:
            for cvIdx in range(3):
                colName = f"{metric}_({cvIdx})"
                metricCols.append(colName)
                self.sample_[colName] = np.nan
        # add metric columns to column dictionary
        self.colNames_['metrics'] = metricCols
        self.colNames_['all'] += metricCols

    def _makeModel(self, *args, **kwargs):
        NotImplemented

    def _runScenario(self, *args, **kwargs):
        NotImplemented

    #===========================================================================#
    # semi-private                                                              #
    #===========================================================================#
