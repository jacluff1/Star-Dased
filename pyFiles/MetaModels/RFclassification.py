
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from StarDased.pyFiles.BaseClass import BaseClass
from MLbase import MLbase

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
        self.model_.fit(self.data_['train'].X(), self.data_['train'].Y())

    def predict(self):
        for key in ['train', 'validate', 'test']:
            X = self.data_[key].X()
            Yhat = self.model_.predict(X)
            self.data_[key].updateYhat(Yhat)

    #===========================================================================#
    # semp-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required by MLbase OR BaseClass                                           #
    #===========================================================================#

    def _buildModel(self, **kwargs):
        """
        https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
        """
        self.model_ = RandomForestClassifier(**kwargs)

    def _getParameterMap(self, **kwargs):
        self.parameterMap_ = inp.RFclassifierParameterMap

    def _runScenario(self, *args):

        if len(args) == 0:
            sampleRowIdx = self.sampleRowIdx_
        if len(args) == 1:
            sampleRowIdx = args[0]

        # model hyperpareters from sample
        params = self._findModelParams(sampleRowIdx)

        # construct model
        self._buildModel(**params)

        # train model with training data
        self.fit()

        # make predicitons on all data sets
        self.predict()

        # calculate the accuracies, precision, and recall
        accuracy = self.performanceAccuracy()
        precision = self.performancePrecision()
        recall = self.performanceRecall()

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
