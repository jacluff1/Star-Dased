
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from BaseClass import BaseClass
from Input import radiusParams, thetaParams, phiParams

import Functions as fun

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import numpy as np
import pandas as pd
import pdb

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class Simulation( BaseClass ):

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__( self, *args, **kwargs ):
        """
        use:
        creates an instance of Simulation. defines a factor space based on
        params defined in Input.py. If the sim has not been previously run, will
        create an empty DataFrame to hold all the sim data.

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

        # construct smaller set of kwargs used for construction
        kwargs1 = {}
        if 'verbose' in kwargs: kwargs1['verbose'] = kwargs['verbose']

        # run BaseClass constructor for Simulation instance
        super().__init__( "Simulation", *args, **kwargs )

    #===========================================================================#
    # public methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # puplic methods                                                            #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def run( self, *args, **kwargs ):
        """
        use:
        Method shall include the general instructions to populate self.data_,
        including running through each random walk scenario set up in the
        sample. For sim models this means generating sim data; for meta models
        this means generating results from different model hyper-parameters,
        which is used to find the best set of hyper-parameters for the meta
        model.

        For all scenarios, this method will make sure the following are recorded
        on the appropriate row in self.data_:
        1) initial state factors
        2) any calculated or generated factors/input
        3) the output of the run

        After each scenario, the current model will be:
        1) the factorState will updated, if result is better than previous
        result
        2) the randomWalkCounter will either be incremented or reset to 0
        3) the model state will be saved ( self.saveState() )

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
    # semi-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def _generateEmptyData( self, **kwargs ):
        """
        use:
        Method shall add an empty pd.DataFrame, accessed by self.data_. the
        DataFrame will hold all the generated data from all the random walks
        from all the initial states defined in the generated sample ( found in
        self.sample_ )

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
        self.data_ = pd.DataFrame( columns=self.columns_ )
        self._setInitialFactorState( 0, **kwargs )

    def _generateFactorSpace( self, **kwargs ):
        """
        use:
        Method shall add a dictionary, accessed by self.factorSpace_, where the keys
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

    def _generateSampleFactors( self, **kwargs ):
        """
        use:
        Method shall add a pd.DataFrame, accessed by self.sample_ that has columns:
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

        # find initial factors from list of factors
        sampleFactors = []
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
                    sampleFactors.append( x )

        # create DataFrame
        df = pd.DataFrame(
        index   = np.arange( len(sampleFactors) )   ,
        columns = [ 'column', 'minIdx', 'midIdx', 'maxIdx' ]  ,
        )

        # fill in the DataFrame
        df.column = sampleFactors
        df.minIdx = 0
        for rowIdx, column in enumerate( df.column ):
            if 'radius' in column:
                maxIdx = radiusParams[2]
            elif 'theta' in column:
                maxIdx = thetaParams[2]
            elif 'phi' in column:
                maxIdx = phiParams[2]
            df.loc[ rowIdx, 'maxIdx' ] = maxIdx
            df.loc[ rowIdx, 'midIdx' ] = maxIdx // 2

        # add sample factor DataFrame
        self.sampleFactors_ = df

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#

    def __generateScenario( self, *args, **kwargs ):
        """
        use:
        use the current 'factorState', generate the remaining necessary input
        for a scenario, and add input to 'data'

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

        #
        pass
