
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

        # if no sim data is found, create empty pd.DataFrame to hold them
        if not hasattr( self, 'simData_' ):
            self.simData_ = pd.DataFrame( columns=self.columns_ )

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

    def __generateScenario( self, *args, **kwargs ):
        """
        use:
        generates random stars, calculates initial velocities for each star
        using escape velocity for

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

        pass
