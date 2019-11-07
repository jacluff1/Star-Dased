
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

# import class definitions
from pyFiles.BaseClass import BaseClass
from pyFiles.MetaModels.DataSet import DataSet
import pyFiles.Functions as fun
import pyFiles.Input as inp

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import itertools
import numpy as np
import pandas as pd

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class MLbase(BaseClass):

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__(self, name, *args, **kwargs):

        # set hyper-parameter map only if it doesn't exist yet
        if not hasattr(self, 'parameterMap_'): self._getParameterMap(**kwargs)

        # construct smaller set of kwargs used for construction
        kwargs1 = {}
        if 'verbose' in kwargs: kwargs1['verbose'] = kwargs['verbose']

        # run BaseClass constructor for Simulation instance
        super().__init__(name, *args, **kwargs)

        # add DataFrame sim data if not present
        if not hasattr(self, 'data_'): self._splitData()

        # add estimator index (index of estimator column of primary concern)
        if not hasattr(self, 'estIdx_'): self.estIdx_ = 2

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
            results[key] = self.data_[key].accuracy_
        return results

    def performancePrecision(self):
        results = {}
        for key in ['train', 'validate', 'test']:
            results[key] = self.data_[key].precision_[0, self.estIdx_]
        return results

    def performanceRecall(self):
        results = {}
        for key in ['train', 'validate', 'test']:
            results[key] = self.data_[key].recall_[0, self.estIdx_]
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
        metric = kwargs['metric'] if 'metric' in kwargs else 'sum'
        # metrics available
        metrics = ['accuracy', 'precision', 'recall']
        # validation column names for each metric
        valCols = [f"{x}_(1)" for x in metrics]
        # find validate metric column
        if metric == 'sum':
            metricCol = metric
            # create metric column by summing the validation entries for each available metric.
            self.sample_[metric] = self.sample_[valCols].sum(axis=1)
        elif metric in ['accuracy', 'precision', 'recall']:
            metricCol = f"{metric}_(1)"
        else:
            raise KeyError("OOPSIE! you seem to have entered a metric value incorrectly, or have selected a metric that isn't yet implemented.\ntry entries like: 'accuracy', 'precision', 'recall', or 'sum'.")
        # find the row index with the maximum value in the chosen metric column
        sampleRowIdx = self.sample_[metricCol].idxmax()
        # re-run the best scenario to update all relevant data
        self._runScenario(sampleRowIdx, **kwargs)

    def _findModelParams(self, sampleRowIdx):
        # get the row from the sample DF
        sampleRow = self.sample_.iloc[sampleRowIdx]
        # find model hyperparameters
        params = {key:sampleRow[key] for key in self.parameterMap_.keys()}
        # replace any pandas NaN with native None
        for key,val in params.items():
            if str(val).lower() == 'nan': params[key] = None
        # add in the number of estimators
        params['n_estimators'] = len(self.colNames_['estimators'])
        # enforce data types
        params['min_samples_leaf'] = int(params['min_samples_leaf'])
        # return model hyperparameters
        return params

    def _splitData(self, **kwargs):

        # set variables by key word arguments
        trainP = kwargs['trainP'] if 'trainP' in kwargs else 0.6
        valP = kwargs['valP'] if 'valP' in kwargs else 0.2
        seed = kwargs['seed'] if 'seed' in kwargs else 0

        # collect percentages of how data will be split
        splitPercentage = {'train':trainP, 'validate':valP, 'test':1-trainP-valP}

        # load generated sim data
        df = pd.read_csv("data/Simulation.csv")

        # collect the row indicies where the outcome is different
        idxEst = {colName:df[df[colName]==1].index.values for colName in self.colNames_['estimators']}

        # shuffle all the indicies
        np.random.seed(seed)
        for idx in idxEst.values(): np.random.shuffle(idx)

        # collect the number of rows associtated with each estimator outcome
        nEst = {key:val.size for key,val in idxEst.items()}

        # create empty containers to hold index arrays associated with each dataset
        idxDs = {key:[] for key in ['train', 'validate', 'test']}

        for colName in self.colNames_['estimators']:
            # get the number from each estimator being divyied up between datasets
            Nds = {dsName:int(nEst[colName]*splitPercentage[dsName]) for dsName in ['train', 'validate', 'test']}
            # slice index arrays from estimates and add them to idxDs collection
            idxDs['train'] = idxEst[colName][:Nds['train']]
            idxDs['validate'] = idxEst[colName][Nds['train']:Nds['train']+Nds['validate']]
            idxDs['test'] = idxEst[colName][Nds['train']+Nds['validate']:]

        # merge list of index arrays for each dataset into single array of indices
        for dsName,idxList in idxDs.items(): idxDs[dsName] = np.hstack(idxList)

        # make a column that collects the one-hotted estimator columns into a single column of discrete values
        # df['y'] = df[self.colNames_['estimators']].to_numpy(np.int32).argmax(axis=1)

        # collect the Xcols and Ycols
        Xcols = list(inp.controlFactors.keys()) + inp.randomFactors
        Ycols = self.colNames_['estimators']
        # Ycols = ['y']

        # add dictionary of split data
        self.data_ = {dsName:DataSet(df.iloc[idx], Xcols, Ycols) for dsName,idx in idxDs.items()}

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
            list(itertools.product(*self.parameterMap_.values())),
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
