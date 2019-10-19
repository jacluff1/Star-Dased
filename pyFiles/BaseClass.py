
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
        if 'nTreatments' in kwargs: kwargs1['nTreatments'] = kwargs.pop( 'nTreatments' )
        numReplicates = kwargs.pop( 'numReplicates' ) if 'numReplicates' in kwargs else 32

        # look for any previously saved state and load it if it exists
        self.loadState( **kwargs1 )

        # generating sample space every time, will alow factor space to be
        # updated at any time without destroying previous results
        self._generateSampleSpace( **kwargs1 )

        # only generate metadata if it doesn't already exist
        if not hasattr( self, 'factors_' ):
            self._generateMetaData( *args, **kwargs1 )

        # only generate a sample if it doesn't already exist
        if not hasattr( self, 'sample_' ):
            self._importSample( **kwargs1 )

        # only generate empty data if none exist
        if not hasattr( self, 'data_' ):
            self._generateEmptyData( **kwargs1 )

        # only add the number of replicates if it doesn't already exist
        if not hasattr( self, 'numReplicates_' ):
            self.numReplicates_ = numReplicates

        # only add Monte Carlo replicate counter if it doesn't exist
        if not hasattr( self, 'replicateCounter_' ): self.replicateCounter_ = 0

        # only add sample row index it doesn't already exist
        if not hasattr( self, 'sampleRowIdx_' ): self.sampleRowIdx_ = 0

        # only add flag for run complete it doesn't already exist
        if not hasattr( self, 'runComplete_' ): self.runComplete_ = False

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
        """
        use:
        This method runs through each treatment in sample_ and terminates when
        __runTreatment() sets runComplete_ = True

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        while not self.runComplete_:
            # run the treatement for current treatement, specified by
            # sampleRowIdx
            self._runTreatment()
            # increment sampleRowIdx
            self.sampleRowIdx_ += 1
            # evaluate run completion conditions, if the sample row index is
            # greater than the number of rows in sample_
            self.runComplete_ = ( self.sampleRowIdx_ > self.sample_.shape[ 0 ] )

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

    def _generateMetaData( self, *args, **kwargs ):
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

    def _runTreatment( self, **kwargs ):
        """
        run Monte Carlo scenarios for the given replicate
        """

        # treatment number
        n1 = self.sampleRowIdx_ + 1

        fun.printHeader(*[
            "",
            f"treatment:\t{n1} / {self.sample_.shape[0]}",
        ], verbose = True )

        while self.replicateCounter_ < self.numReplicates_:
            # replicate number
            n2 = self.replicateCounter_ + 1
            print( f"replicate:\t{n2} / {self.numReplicates_}" )
            # run monte carlo scenario
            self._runMonteCarloScenario( **kwargs )
            # increment replicate counter
            self.replicateCounter_ += 1
            # save sim state
            self.saveState( **kwargs )

        # reset the replicate counter for next treatment
        self.replicateCounter_ = 0

    #===========================================================================#
    # semi-protected                                                            #
    # any methods defined here need to be implemnted in the child class         #
    #===========================================================================#

    def _generateEmptyData( self ):
        """
        use:
        The child class needs to define this class for itself. However, it
        shall add an empty pd.DataFrame, accessed by self.data_. the DataFrame
        will hold all the generated data from all the random walks from all the
        initial states defined in the generated sample ( found in self.sample_ )

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        NotImplemented

    def _runMonteCarloScenario( self, *args, **kwargs ):
        """
        do everything required to run an individual monte carlo scenario for
        a specific treatement
        """
        NotImplemented

    #===========================================================================#
    # semi-private methods                                                      #
    # child class can only access theese methods, in whole or in part, by using #
    # super()                                                                   #
    #===========================================================================#

    # depricated, use for new method decoding sample to use for sim
    # def __generateLatinHCsample( self, *args, **kwargs ):
    #     """
    #     generate latin hyper-cube as pd.DataFrame and save it as sample_
    #     """
    #
    #     nTreatments = kwargs['nTreatments'] if 'nTreatments' in kwargs else len( self.sampleFactors_ )
    #
    #     # construct basic latin hypercube using pyDOE
    #     lhs = pyDOE.lhs(
    #         nTreatments, # the number of treatments
    #         criterion = "corr" # minimize the maximum correlation coefficient
    #     )
    #
    #     # organize columns into a lookup-dictionary
    #     columns = { col : idx for ( idx , col ) in enumerate( self.sampleFactors_ ) }
    #
    #     # create dictionary to collect results
    #     results = {}
    #
    #     # go through each column in the sample factors and ajust it to reflect
    #     # sim values
    #     for colName, colIdx in columns.items():
    #
    #         # for all columns except radius, have the new value be old value
    #         # scaled and shifted to reflect the range between the min & max of
    #         # the desired values
    #         if 'mass' in colName:
    #             lhs[ : , colIdx ] *= ( massParams[1] - massParams[0] )
    #             lhs[ : , colIdx ] += massParams[0]
    #         elif 'theta' in colName.lower():
    #             lhs[ : , colIdx ] *= ( thetaParams[1] - thetaParams[0] )
    #             lhs[ : , colIdx ] += thetaParams[0]
    #         elif 'phi' in colName.lower():
    #             lhs[ : , colIdx ] *= ( phiParams[1] - phiParams[0] )
    #             lhs[ : , colIdx ] += phiParams[0]
    #         # for all the radius columns, convert to exponential pdf
    #         elif 'radius' in colName:
    #             # lhs[ : , colIdx ] *= ( np.log( radiusParams[1] ) - np.log( radiusParams[0] ))
    #             # lhs[ : , colIdx ] + np.log( radiusParams[0] )
    #             # lhs[ : , colIdx ] = np.exp( lhs[ : , colIdx ] )
    #             lhs[ : , colIdx ] *= ( radiusParams[1] - radiusParams[0] )
    #             lhs[ : , colIdx ] += radiusParams[0]
    #         # add the column to results
    #         results[ colName ] = lhs[ : , colIdx ]
    #
    #     # convert lhs to pd.DataFrame
    #     df = pd.DataFrame( results )
    #
    #     # add sample
    #     self.sample_ = df
