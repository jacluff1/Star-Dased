
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from pyFiles.BaseClass import BaseClass
from pyFiles.MetaModels.MLbase import MLbase

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

from sklearn.ensemble import RandomForestClassifier

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class RandomForests(BaseClass, MLbase):

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__(self, *args, **kwargs):
        super().__init__('RandomForestClassifier', *args, **kwargs)

    #===========================================================================#
    # puplic methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # public methods                                                            #
    # required by MLbase OR BaseClass                                           #
    #===========================================================================#

    def fit(self):
        # fit with training data only
        self.model_.fit()

    def predict(self):

        # make predictions for all DF in data

        predictions = {
            'train': NotImplemented,
            'validate': NotImplemented,
            'test': NotImplemented,
        }
        return predictions

    #===========================================================================#
    # semp-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required by MLbase OR BaseClass                                           #
    #===========================================================================#

    def _getParameterMap(self, **kwargs):
        self.parameterMap_ = inp.RFclassifierParameterMap

    def _makeModel(self, **kwargs):
        """
        https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
        """
        self.model_ = RandomForestClassifier(**kwargs)

    def _runScenario(self):

        # get hyper-parameters from sample
        sampleRow = self.sample_.iloc[self.sampleRowIdx_]

        # extract model kwargs from sample row
        kwargs = {key:sampleRow[key] for key in self.parameterMap_.keys()}

        # construct model
        self._makeModel(**kwargs)

        # train model with training data
        self.fit()

        # make predicitons on all data sets
        predictions = self.predict()

        # calculate the accuracies, precision, and recall
        accuracy = self._performanceAccuracy(predictions)
        precision = self._performancePrecision(predictions)
        recall = self._performanceRecall(predictions)

        # record accuracy (and another other desired metric) for both train and
        # validate sets
        for metricName, metricDict in zip(['accuracy', 'precision', 'recall'], [accuracy, precision, recall]):
            for cvIdx, key in enumerate(['train', 'validate', 'test']):
                colName = f"{metricName}_({cvIdx})"
                self.sample_.loc[self.sampleRowIdx_, colName] = metricDict[key]

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":

    # add argparser

    RFc = RandomForestClassifier()
    RFc.run()
