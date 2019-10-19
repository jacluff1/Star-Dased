
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
from Input import radiusParams, thetaParams, phiParams, massParams

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

from copy import deepcopy
import numpy as np
import pandas as pd
import pdb
import pyDOE
from scipy.stats.distributions import expon

#===============================================================================#
# BaseClass definition                                                          #
#===============================================================================#

class BaseClass:

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__( self, name, *args, **kwargs ):
        """
        use:
        instructions on how to perform basic construction for any class instance
        that inherits BaseClass. Will look for saved state based on name
        provided; if it finds a saved state, will load it. any items in **kwargs
        are added as attributes.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:
        name            str             instance name is used to save/load state
                                        as well as descriptive printing to
                                        terminal
        *args           tuple, str      column names to use as estimators, if
                                        metadata needs to be generated.

        kwargs:

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """

        # assign name as attribute
        self.name_ = name

        # take out any key word arguments which aren't desired as attributes
        kwargs1 = {}
        if 'verbose' in kwargs: kwargs1['verbose'] = kwargs.pop( 'verbose' )
        if 'addTail' in kwargs: kwargs1['addTail'] = kwargs.pop( 'addTail' )

        # look for any previously saved state and load it if it exists
        self.loadState( **kwargs1 )

        # only generate metadata if it doesn't already exist
        if not hasattr( self, 'factors_' ):
            self._generateColumnNames( *args, **kwargs1 )

        # only generate a sample if it doesn't already exist
        if not hasattr( self, 'sample_' ):
            self._getSample( **kwargs1 )

        # only generate empty data if none exist
        if not hasattr( self, 'data_' ):
            self._generateEmptyData( **kwargs1 )

        # add any remaining kwargs as attributes, will override previous state
        # if any keys conflict
        self._dict2attributes( kwargs, message="Overriding Attributes", **kwargs1 )

    #===========================================================================#
    # public methods                                                            #
    # any methods defined here will be able to be used directly by its          #
    # children, make sure any attributes added by the methods below are present #
    # in the child class.                                                       #
    #===========================================================================#

    def loadState( self, **kwargs ):
        """
        use:
        looks for previously saved state and loads it into instance attributes
        if it exists.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """
        state = fun.fromPickle( self.name_, **kwargs )
        self._dict2attributes( state, message='Loading State:', **kwargs )

    def saveState( self , **kwargs ):
        """
        use:
        saves the current state of the model instance into a pickle, which will
        automatically be loaded up by the constructor next time it is
        instantiated.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """
        fun.toPickle( self.name_, self.__dict__, **kwargs )

    #===========================================================================#
    # public methods                                                            #
    # any methods defined here need to be implemnted in the child class         #
    #===========================================================================#

    def run( self, *args, **kwargs ):
        NotImplemented

    #===========================================================================#
    # semi-protected methods                                                    #
    # any methods defined here will be able to be used directly by its          #
    # children, make sure any attributes added by the methods below are present #
    # in the child class.                                                       #
    #===========================================================================#

    def _dict2attributes( self, dictionary, **kwargs ):
        """
        use:
        saves every item in dictionary as an attribute

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """

        addTail = kwargs['addTail'] if 'addTail' in kwargs else False

        fun.printDict( dictionary, **kwargs )
        if len( dictionary ) > 0:
            for key,value in dictionary.items():
                if addTail:
                    setattr( self, f"{key}_", value )
                else:
                    setattr( self, key, value )

    def _generateColumnNames( self, *args, **kwargs ):
        """
        use:
        adds list of all columns, factor space columns, estimator columns,
        number of factors, and number of estimators

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:
        *args           tuple, str      column name(s) of estimators

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        # estimators are the args provided or 'runTime' by default
        if len( args ) > 0:
            estimators = list( args )
        else:
            estimators = [ 'runTime' ]

        # create a container to hold all the: sample factors, random factors,
        # and final factors
        sampleFactors     = []
        monteCarloFactors = []
        finalFactors      = []

        # fill in the sample factors
        for starIdx in [ 0, 1, 2 ]:
            sampleFactors.append( f"mass_({starIdx})" )
        for name in [ 'radius', 'theta', 'phi', 'velTheta', 'velPhi' ]:
            for starIdx in [ 0, 1, 2 ]:
                for timeIdx in [ 0, -1 ]:
                    colName = f"{name}_({starIdx},{timeIdx})"
                    if timeIdx == 0:
                        sampleFactors.append( colName )
                    else:
                        finalFactors.append( colName )

        # fill in the monte carlo factors
        for name in [ 'speed' ]:
            for starIdx in [ 0, 1, 2 ]:
                for timeIdx in [ 0, -1 ]:
                    colName = f"{name}_({starIdx},{timeIdx})"
                    if timeIdx == 0:
                        monteCarloFactors.append( colName )
                    else:
                        finalFactors.append( colName )

        # other columns, usefull for EDA and tracking
        miscFactors = [ 'treatment', 'replicate' , "outcome", 'steps' ]

        # add columns
        self.estimators_        = estimators
        self.sampleFactors_     = sampleFactors
        self.monteCarloFactors_ = monteCarloFactors
        self.finalFactors_      = finalFactors
        self.factors_           = sampleFactors + monteCarloFactors + finalFactors + miscFactors
        self.miscFactors_       = miscFactors
        self.columns_           = estimators + self.factors_

        # add numbers of columns
        self.numEstimators_         = len( estimators )
        self.numSampleFactors_      = len( sampleFactors )
        self.numMonteCarloFactors_  = len( monteCarloFactors )
        self.numFactors_            = len( self.factors_ )
        self.numColumns_            = len( self.columns_ )

    #===========================================================================#
    # semi-protected                                                            #
    # any methods defined here need to be implemnted in the child class         #
    #===========================================================================#

    def _generateEmptyData( self ):
        NotImplemented

    def _getSample( self, *args, **kwargs ):
        NotImplemented

    #===========================================================================#
    # semi-private methods                                                      #
    # child class can only access theese methods, in whole or in part, by using #
    # super()                                                                   #
    #===========================================================================#
