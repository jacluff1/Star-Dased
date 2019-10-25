
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from pyFiles.MetaModels.MLbase import MLbase

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class RandomForests(MLbase):

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

    #===========================================================================#
    # semp-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required by MLbase OR BaseClass                                           #
    #===========================================================================#

    def _getParameterMap(self, **kwargs):
        """
        n_estimators=’warn’, criterion=’gini’, max_depth=None, min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=’auto’, max_leaf_nodes=None, min_impurity_decrease=0.0, min_impurity_split=None, bootstrap=True, oob_score=False, n_jobs=None, random_state=None, verbose=0, warm_start=False, class_weight=None
        """
        self.parameterMap_ = {
            'n_estimators' = [1, 10, 20, 50, 100, 200, 5000],
            'max_depth' = [None] + [x for x in range(10)],
            'min_samples_leaf' = [x for x in range(3)]
        }

    def _runScenario(self):
        NotImplemented

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#
