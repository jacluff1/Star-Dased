
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

        # look for any previously saved state and load it if it exists
        self.loadState( **kwargs1 )

        # generating factor space every time, will alow factor space to be
        # updated at any time without destroying previous results
        self.__generateFactorSpace( **kwargs1 )

        # only generate sample factors if it doesn't already have them
        if not hasattr( self, 'sampleFactors_' ):
            self.__generateSampleFactors( **kwargs1 )

        # only generate metadata if it doesn't already exist
        if not hasattr( self, 'factors_' ):
            self._generateMetaData( *args, **kwargs1 )

        # only generate empty data if none exist
        if not hasattr( self, 'data_' ):
            self.__generateEmptyData( **kwargs1 )

        # only generate a run schedule if it doesn't already exist
        if not hasattr( self, 'sample_' ):
            self._generateSample( **kwargs1 )

        # add any remaining kwargs as attributes, will override previous state
        # if any keys conflict
        self._dict2attributes( kwargs, message="Overriding Attributes", **kwargs1 )

    #===========================================================================#
    # public methods                                                            #
    # methods below should be safe to use in any child class because it has     #
    # whatever it needs given to it in BaseClass construction.                  #
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

        # start with the column names
        if len( args ) > 0:
            colNames = [ name for name in args ]
        else:
            colNames = [ 'runTime' ]

        # add the estimators
        self.estimators_ = deepcopy( colNames )

        # add the number of estimators
        self.numEstimators_ = len( self.estimators_ )

        # fill in the columns by adding radius, theta, phi, and mass, for
        # all stars for both initial and final times
        for name in [ 'radius', 'theta', 'phi' , 'mass' ]:
            for starIdx in [ 0, 1, 2 ]:
                for timeIdx in [ 0, -1 ]:
                    if name == 'mass':
                        colName = f"{name}_({starIdx})"
                    else:
                        colName = f"{name}_({starIdx},{timeIdx})"
                    colNames.append( colName )

        # add data columns
        self.columns_ = colNames

        # add the factors
        self.factors_ = colNames[ self.numEstimators_ : ]

        # add the number of factors
        self.numFactors_ = len( self.factors_ )

    def _generateSample( self, *args, **kwargs ):
        """
        use:
        generates a pd.DataFrame that the samples for random walk scenarios.

        right now only includes starting at the extrema ( 2 ) and at the
        centroid ( 1 ). Perhaps look into a latin hypercube or some other
        sampling technique.

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

        # create an empty pd.DataFrame
        df = pd.DataFrame(
            index   = np.arange( 3 ),
            columns = [ 'started', 'finished' ] + self.sampleFactors_
        )

        # make sure all started and finished = 0
        df.started  = 0
        df.finished = 0

        # first in the sample is the centroid
        for col in self.sampleFactors_:
            if   'radius' in col:
                idx = radiusParams[2] // 2
            elif 'theta'  in col:
                idx = thetaParams[2]  // 2
            elif 'phi'    in col:
                idx = phiParams[2]    // 2
            df.loc[ 0, col ] = idx
        # second in the sample is all minima
        for col in self.sampleFactors_: df.loc[ 1 , col ] = 0
        # third in the sample is all maxima
        for col in self.sampleFactors_: df.loc[ 2 , col ] = -1

        self.sample_ = df

    def _randomWalk( self, *args, **kwargs ):
        """
        use:

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

        # set variables from key word arguments
        step = kwargs['step'] if 'step' in kwargs else True

        # if a random step is needed (ie all steps except the first in a sample
        # scenario) generate a random step
        if step:

            while True:

                # randomly pick to either decrement (0) or incremenet (1)
                increment = bool( np.random.randint(2) )

                if increment:
                    # create a mask for all the initial factors that can be incremented
                    mask = []
                    pass

                else:
                    # create a mask for all the initial factors that can be decrimented
                    pass
        pass

    def _setInitialFactorState( self, *args, **kwargs ):
        """
        use:

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:
        sampleIdx       int             row number from self.sample_ used to set
                                        state

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        # set variable from args
        if len( args ) == 1:
            sampleIdx = args[0]
        elif len( args ) == 0:
            sampleIdx = 0

        # set the initial factor state by extracting factor space indicies from
        # designated row in sample
        self.factorState_ = {
            col : self.sample_.loc[ sampleIdx, col ] for col in self.sampleFactors_
        }

        # also set/reset random walk counter to 0
        self.randomWalkCounter = 0

    #===========================================================================#
    # semi-private methods                                                      #
    # any method here would have to be implemented separately in the specific   #
    # class definition inheriting it.                                           #
    #===========================================================================#

    def __generateEmptyData( self ):
        NotImplemented

    def __generateFactorSpace( self, **kwargs ):
        NotImplemented

    def __generateSampleFactors( self, **kwargs ):
        NotImplemented
