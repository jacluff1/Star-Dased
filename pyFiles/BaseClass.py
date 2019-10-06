
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
from Input import radiusParams, thetaParams, phiParams

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

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
        self._generateFactorSpace( **kwargs1 )

        # only generate metadata if it doesn't already exist
        if not hasattr( self, 'factors_' ): self._generateMetaData( *args, **kwargs1 )

        # only generate a run schedule if it doesn't already exist
        if not hasattr( self, 'sample_' ):
            self._generateSample( **kwargs1 )

        # add any remaining kwargs as attributes, will override previous state
        # if any keys conflict
        self._dict2attributes( kwargs, message="Overriding Attributes", **kwargs1 )

    #===========================================================================#
    # public methods                                                            #
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

    def _generateFactorSpace( self, **kwargs ):
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
        self.factorSpace_ = {
            # having radii in exponential space will allow denser sampling
            # at small radii and sparser sampling at the upper limits of radii
            # this assumes that smaller radii from CM is more likely.
            'radius'    : np.exp( -np.linspace(
                np.log( radiusParams[0] ),
                np.log( radiusParams[1] ),
                radiusParams[2]
            ) )                                                         ,
            # uniform spacing of polar angles assumes all angles are equally
            # likely
            'theta'     : np.linspace( *thetaParams, endpoint=False )   ,
            # uniform spacing of azimuthal angles assumes all angles are equally
            # likely
            'phi'       : np.linspace( *phiParams  , endpoint=False )   ,
        }

        lines = [
            "", 'Factor Space:', "", f"radius:\t{radiusParams}",
            f"theta:\t{thetaParams}", f"phi:\t{phiParams}"
        ]
        fun.printHeader( *lines, **kwargs )

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
        colNames = [ name for name in args ]

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
        self.factors_ = colNames[ len( args ) : ]

        # add the number of factors
        self.numFactors_ = len( self.factors_ )

        # add estimator columns
        self.estimator_ = colNames[ : len( args ) ]

        # add the number of estimator factors
        self.numEstimators_ = len( self.estimator_ )

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

        # find initial factors from list of factors
        self.sampleFactors_ = []
        for x in self.factors_:
            # select string of tuple only
            x1 = x[ x.find( "_" ) + 1 : ]
            # replace '(' with whitespace
            x1 = x1.replace( "(", "" )
            # replace ')' with whitespace
            x1 = x1.replace( ")", "" )
            # split string on commas into list of strings
            x1 = x1.split( "," )
            # convert into a tuple of int
            x1 = tuple([ int( x2 ) for x2 in x1 ])
            # only select tuples of length 2: mass is randomly selected
            if len( x1 ) == 2:
                # only select where the second tuple is 0 (-1 signifies ending
                # value)
                if x1[ 1 ] == 0:
                    # append original factor column
                    self.sampleFactors_.append( x )


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

    def _randomWalk( self, *args , **kwargs ):
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
        pass

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#
