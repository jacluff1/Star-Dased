
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from BaseClass import BaseClass

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import pandas as pd

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
    # puplic methods                                                            #
    #===========================================================================#

    def runSim( self, *args, **kwargs ):
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
    # semi-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#

    def __generateEmptyData( self, **kwargs ):
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
        self.data_ = pd.DataFrame( columns=self.columns_ )
        self._setInitialFactorState( 0, **kwargs )

    def __generateFactorSpace( self, **kwargs ):
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

    def __generateSampleFactors( self, **kwargs ):
        """
        use:
        generate a pd.DataFrame that has columns:
        [ 'column', 'minIdx', 'maxIdx' ]

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
            columns = [ 'column', 'minIdx', 'maxIdx' ]  ,
        )

        # fill in the DataFrame
        df.column = sampleFactors
        df.minIdx = 0
        for rowIdx, column in enumerate( df.column ):
            if 'radius' in column:
                maxIdx = radiusParams[1]
            elif 'theta' in column:
                maxIdx = thetaParams[1]
            elif 'phi' in column:
                maxIdx = phiParams[1]
            df.loc[ rowIdx, 'maxIdx' ] = maxIdx

        # add sample factor DataFrame
        self.sampleFactors_ = df

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
