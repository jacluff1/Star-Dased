
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
        if not hasattr(self, 'data_'):
            if len(args) == 1:
                self.data_ = args[0]
            elif len(args) == 0:
                raise AssertionError, "Need generated sim Data given in args!"

    #===========================================================================#
    # public methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # puplic methods                                                            #
    # required by BaseClass, implemented here                                   #
    # OR                                                                        #
    # required for MLbase, child needs to implement                             #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

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
        for colName in self.colNames_['estimators']: self.sample_[colName] = np.nan

    def _runScenario(self, *args, **kwargs):
        NotImplemented

    #===========================================================================#
    # semi-private                                                              #
    # sampling                                                                  #
    #===========================================================================#
