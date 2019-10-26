
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

    def run(self, **kwargs):
        # use run from baseclass
        super().run(**kwargs)
        # once basic run is complete, find the best model from sample and build
        # it
        self._buildBestModel(**kwargs)

    def performanceAccuracy(self):
        results = {}
        for key in ['train', 'validate', 'test']:
            Y = self.data_[key].Y()
            Yhat = self.data_[key].Yhat()
            results[key] = fun.accuracy(Y, Yhat)
        return results

    def performancePrecision(self):
        results = {}
        for key in ['train', 'validate', 'test']:
            Y = self.data_[key].Y()
            Yhat = self.data_[key].Yhat()
            results[key] = fun.precision(Y, Yhat)
        return results

    def performanceRecall(self):
        results = {}
        for key in ['train', 'validate', 'test']:
            Y = self.data_[key].Y()
            Yhat = self.data_[key].Yhat()
            results[key] = fun.recall(Y, Yhat)
        return results

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

    def _buildBestModel(self, *args, **kwargs):
        # set variables by key word arguments
        metric = kwargs['metric'] if 'metric' in kwargs else 'accuracy'
        # find validate metric column
        metric += "_(1)"
        # find a filtered view of sample that has best validate metric
        df = self.sample_[self.sample_[metric] == self.sample_[metric].max()]
        # make sure df only has one result
        assert df.shape[0] == 1, f"it seems {metric} has multiple best results"
        # get the sample row index that hold best model hyperpareters
        sampleRowIdx = df.index[0]
        # re-run the best scenario to update all relevant data
        self._runScenario(sampleRowIdx, **kwargs)

    def _findModelParams(self, sampleRowIdx):
        # get the row from the sample DF
        sampleRow = self.sample_.iloc[sampleRowIdx]
        # find model hyperparameters
        params = {key:sampleRow[key] for key in self.parameterMap_.keys()}
        # return model hyperparameters
        return params

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

    def _buildModel(self, *args, **kwargs):
        NotImplemented

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

    def _runScenario(self, *args, **kwargs):
        NotImplemented

    #===========================================================================#
    # semi-private                                                              #
    #===========================================================================#
