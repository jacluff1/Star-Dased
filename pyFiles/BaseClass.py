
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

        # look for any previously saved state and load it if it exists
        self.loadState( **kwargs1 )

        # generating factor space every time, will alow factor space to be
        # updated at any time without destroying previous results
        self._generateFactorSpace( **kwargs1 )

        # only generate metadata if it doesn't already exist
        if not hasattr( self, 'factors_' ):
            self._generateMetaData( *args, **kwargs1 )

        # only generate sample factors if it doesn't already have them
        if not hasattr( self, 'sampleFactors_' ):
            self._generateSampleFactors( **kwargs1 )

        # only generate a run schedule if it doesn't already exist
        if not hasattr( self, 'sample_' ):
            self._generateSample( **kwargs1 )

        # only generate empty data if none exist
        if not hasattr( self, 'data_' ):
            self._generateEmptyData( **kwargs1 )

        # only add if it doesn't already exist
        if not hasattr( self, 'sampleRowIdx_' ): self.sampleRowIdx_ = 0

        # only add if it doesn't already exist
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

    def run( self, *args, **kwargs ):
        """
        use:
        Method shall include the general instructions to populate self.data_,
        including running through each random walk scenario set up in the
        sample. For sim models this means generating sim data; for meta models
        this means generating results from different model hyper-parameters,
        which is used to find the best set of hyper-parameters for the meta
        model.

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
            self._runScenario()
            self._updateFactorState()
            self.randomWalk()
            self.saveState()

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
            colNames = list( args )
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
            columns = self.sampleFactors_.column
        )

        # first in the sample is the centroid
        for col in self.sampleFactors_.column:
            if   'radius' in col:
                idx = radiusParams[2] // 2
            elif 'theta'  in col:
                idx = thetaParams[2]  // 2
            elif 'phi'    in col:
                idx = phiParams[2]    // 2
            else:
                pdb.set_trace()
            df.loc[ 0, col ] = idx
        # second in the sample is all minima
        for col in self.sampleFactors_.column: df.loc[ 1 , col ] = 0
        # third in the sample is all maxima
        for col in self.sampleFactors_.column: df.loc[ 2 , col ] = -1

        self.sample_ = df

    def _randomWalk( self, *args, **kwargs ):
        """
        use:
        This method checks that randomWalkCounter <= counterLimit. if
        randomWalkCounter > counterLimit, increment sampleRowIdx,
        _setInitialFactorState, and skip the rest of randomWalk.

        if marking current sample as completed, also check if there are any
        rows in sampe_ not marked completed. If all are completed, set
        runComplete_ to True.

        randomly increment or decrement the current state by one index in the
        factor space of a random initial factor that can be incremented/
        decrimented. If there are no factors that can be incremented, a random
        factor will be decremented; if there are no factors that can be
        incremented, a random factor will be decremented.

        ============================================================================
        input:          type:           description:
        ============================================================================
        args:           type:           description:

        kwargs:         type:           description:
        counterLimit    int             if randomWalkCounter reaches this number
                                        reset this number to 0 and set inital
                                        state to the next sample. Default = 30
        verbose         bool            flag to print, default = False

        ============================================================================
        output:         type:
        ============================================================================
        None            None
        """

        # set variables by key word arguments
        counterLimit = kwargs['counterLimit'] if 'counterLimit' in kwargs else 30

        # check that randomWalkCounter <= counterLimit
        if self.randomWalkCounter_ > counterLimit:
            self.sampleRowIdx_ += 1
            self._setInitialFactorState( **kwargs )
            return

        # randomly pick to either decrement (0) or incremenet (1)
        increment = bool( np.random.randint(2) )

        while True:

            if increment:
                # create a list of all factors that can incremented
                factors = []
                for factor,idx in self.factorState_.items():
                    maxIdx = self.sampleFactors_[ self.sampleFactors_.column == factor ].maxIdx.item()
                    if idx < maxIdx: factors.append( factor )

            else:
                # create a list of all factors that can be decremented
                factors = []
                for factor, idx in self.factorState_.items():
                    minIdx = self.sampleFactors_[ self.sampleFactors_.column == factor ].minIdx.item()
                    if idx > minIdx: factors.append( factor )

            # if no factors found, switch increment and try again
            if len( factors ) == 0:
                increment = not increment
                continue
            else:
                break

        # select a random factor from factors
        factor = factors[ np.random.randint( len( factors ) + 1 ) ]

        if increment:
            self.factorState_[ factor ] += 1
        else:
            self.factorState_[ factor ] -= 1

    def _setInitialFactorState( self, *args, **kwargs ):
        """
        use:
        choose a sample from the hypercube of factor space of initial
        parameters: ( radius, polar angle, azimuthal angle ) for each star.

        if any arg is provided, set sampleRowIdx to arg, otherwise use the
        current sampleRowIdx. Set the state based on the the row in sample_
        designated by sampleRowIdx.

        reset randomWalkCounter to 0.

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

        # determine the row to use in sample_ to set state to
        if len( args ) == 1: self.sampleRowIdx_ = args[0]

        # set the initial factor state by extracting factor space indicies from
        # designated row in sample
        self.factorState_ = {
            col : self.sample_.loc[ self.sampleRowIdx_, col ] for col in self.sampleFactors_.column
        }

        # set/reset random walk counter to 0
        self.randomWalkCounter_ = 0

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

    def _generateFactorSpace( self, **kwargs ):
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

    def _generateSampleFactors( self, **kwargs ):
        """
        use:
        The child class needs to define this class for itself. However, it
        shall add a pd.DataFrame, accessed by self.sample_ that has columns:
        [ 'factor', 'minIdx', 'midIdx', 'maxIdx' ]
        The rows shall be the factors being considered in the hypercube defining
        the sample/factor space.

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

    def _runScenario( self, **kwargs ):
        """
        use:
        This method needs to be defined in child class; however this
        method shall:

        1) use the current factorState to calculate/generate any necessary
        additional input
        2) run scenario
        3) record all scenario input output in self.data_

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

    def _updateFactorState( self, *args, **kwargs ):
        """
        use:
        This method needs to be defined in child class; however,
        This method shall look at the last entry ( the current scenario that
        just completed ) and the entry before that, whichever outcome is better
        and either keep the current stateFactor ( the previous result was
        better ), or it will update its stateFactor by taking the sampleFactor
        values from the last row ( the current scenario ).

        if keeping current state, increment randomWalkCounter; if using new
        state, reset randomWalkCounter to 0

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

    #===========================================================================#
    # semi-private methods                                                      #
    # any children wanting to use methods below would need a super() to use     #
    # in whole or in part                                                       #
    #===========================================================================#

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
