
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
from Input import radiusParams, thetaParams, phiParams

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

from copy import deepcopy
import numpy as np
import pandas as pd
import pdb

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
        numReplicates = kwargs.pop( 'numReplicates' ) if 'numReplicates' in kwargs else 20

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
            self._generateSample( **kwargs1 )

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
            self.__runTreatment()
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
        fun.printDict( dictionary, **kwargs )
        if len( dictionary ) > 0:
            for key,value in dictionary.items():
                setattr( self, key + '_', value )

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

        # create a container to hold all the sample factors
        sampleFactors = {
            'all'       : [],
            'initial'   : [],
            'final'     : [],
        }

        # crate containers to hold all the randomly generated factors
        monteCarloFactors = {
            'all'       : [],
            'initial'   : [],
            'final'     : [],
        }

        # fill in the sample factors
        for starIdx in [ 0, 1, 2 ]:
            sampleFactors['all'].append( f"mass_({starIdx})" )
            sampleFactors['initial'].append( f"mass_({star})" )
        for name in [ 'radius', 'theta', 'phi' ]:
            for starIdx in [ 0, 1, 2 ]:
                for timeIdx in [ 0, -1 ]:
                    colName = f"{name}_({starIdx},{timeIdx})"
                    sampleFactors['all'].append( colName )
                    if timeIdx == 0:
                        sampleFactors['initial'].append( colName )
                    else:
                        sampleFactors['final'].append( colName )

        # fill in the monte carlo factors
        for name in [ 'speed', 'velRadial', 'velPolar', 'velAzimuthal' ]:
            for starIdx in [ 0, 1, 2 ]:
                for timeIdx in [ 0, -1 ]:
                    colName = f"{name}_({starIdx},{timeIdx})"
                    monteCarloFactors['all'].append( colName )
                    if timeIdx == 0:
                        monteCarloFactors['initial'].append( colName )
                    else:
                        monteCarloFactors['final'].append( colName )

        # add columns
        self.estimators_        = estimators
        self.sampleFactors_     = sampleFactors
        self.monteCarloFactors  = monteCarloFactors
        self.factors_           = sampleFactors['all'] + monteCarloFactors['all']
        self.columns_           = estimators + self.factors_

        # add numbers of columns
        self.numEstimators_         = len( estimators )
        self.numSampleFactors       = len( sampleFactors )
        self.numMonteCarloFactors   = len( monteCarloFactors )
        self.numFactors_            = len( self.factors_ )
        self.numColumns_            = len( self.columns_ )

    def _generateSample( self, *args, **kwargs ):
        """
        use:
        choose the method for generating a treatment sample.

        Current Options:
        latin (needs implementing)

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:

        kwargs:         type:           description:
        sampleMethod    str             used to choose sampling method
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        method = kwargs['sampleMethod'] if 'sampleMethod' in kwargs else 'latin'

        if method == 'latin':
            self.__generateLatinHCsample( *args, **kwargs )

        else:
            raise KeyError, f"{mehod} hasn't been defined yet!"

    def _runTreatment( self, **kwargs ):
        """
        run Monte Carlo scenarios for the given replicate
        """

        while self.replicateCounter_ < self.numReplicates_:
            # run monte carlo scenario
            self._runMonteCarloScenario( **kwargs )
            # increment replicate counter
            self.replicateCounter_ += 1
            # save sim state
            self.saveState( **kwargs )

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

    def _generateSampleSpace( self, **kwargs ):
        """
        use:
        The child class needs to define this class for itself. However, it
        shall add a dictionary, accessed by self.factorSpace_, where the keys
        are the sampleFactors and the values are np.arrays of all allowed values
        included in the factor space.

        The keys in sampleFactors_ must remain constant, but it is allowed to
        adjust the factor space (for example, expand the factor space, narrow it
        down around a percieved richer space, etc..). Every time the model is
        instantiated, it will retain its previous runs and re-set up the factor
        space it is considering.

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

    def __generateLatinHCsample( self, *args, **kwargs ):
        """
        generate latin hyper-cube as pd.DataFrame and save it as sample_
        """
        NotImplemented
