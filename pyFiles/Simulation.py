
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from BaseClass import BaseClass

import Functions as fun
import Input as inp

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

from copy import deepcopy
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

        # # construct smaller set of kwargs used for construction
        # kwargs1 = {}
        # if 'verbose' in kwargs: kwargs1['verbose'] = kwargs['verbose']
        numReplicates = kwargs.pop( 'numReplicates' ) if 'numReplicates' in kwargs else 32

        # run BaseClass constructor for Simulation instance
        super().__init__( "Simulation", *args, **kwargs )

        # only add the number of replicates if it doesn't already exist
        if not hasattr( self, 'numReplicates_' ):
            self.numReplicates_ = numReplicates

        # only add Monte Carlo replicate counter if it doesn't exist
        if not hasattr( self, 'replicateCounter_' ): self.replicateCounter_ = 0

        # only add sample row index it doesn't already exist
        if not hasattr( self, 'sampleRowIdx_' ): self.sampleRowIdx_ = 0

        # only add flag for run complete it doesn't already exist
        if not hasattr( self, 'runComplete_' ): self.runComplete_ = False

    #===========================================================================#
    # public methods                                                            #
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
            self._runScenario()
            # increment sampleRowIdx
            self.sampleRowIdx_ += 1
            # evaluate run completion conditions, if the sample row index is
            # greater than the number of rows in sample_
            self.runComplete_ = ( self.sampleRowIdx_ > self.sample_.shape[ 0 ] )

    #===========================================================================#
    # puplic methods                                                            #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

    def _runScenario( self, **kwargs ):

        # set up---------------------------------------------------------------#

        # scenario number
        n1 = self.sampleRowIdx_ + 1

        fun.printHeader(*[
            "",
            f"scenario:\t{n1} / {self.sample_.shape[0]}",
        ], verbose = True )

        # use the sampleRowIdx to get treatement values
        sampleRow = self.sample_.iloc[ self.sampleRowIdx_ ]

        # construct SPC positions
        spc_i3 = np.zeros( (3,3) )
        for starIdx in [ 1, 2, 3 ]:
            for coordinateIdx in [ 0, 1, 2 ]:
                colName = f"pos_({starIdx},{coordinateIdx},0)"
                if colName in inp.constantFactors:
                    spc_i3[ starIdx, coordinateIdx ] = constantFactors[ colName ]
                elif colName in sampleRow:
                    spc_i3[ starIdx, coordinateIdx ] = sampleRow[ colName ]
                else:
                    self.__ColumnAssertion( colName )

        # construct masses
        m_i1 = np.zeros( (3,1) )
        for starIdx in [ 1, 2, 3 ]:
            colName = f"mass_({starIdx})"
            if colName in inp.constantFactors:
                m_i1[ starIdx, 0 ] = constantFactors[ colName ]
            elif colName in sampleRow:
                m_i1[ starIdx, 0 ] = sampleRow[ colName ]
            else:
                self.__ColumnAssertion( colName )

        # calculate XYZ positions
        x_i3 = fun.spc2xyz( spc_i3, **kwargs )

        # calculate CM of the new system ( vector from current origin to CM )
        CM_13 = fun.findCM( x_i3, m_i1 )

        # make CM the new origin ( subtract CM vector from star positions )
        x_i3 -= CM_13

        # calculate escape velocity from system
        escapeSpeed_i1 = fun.escapeSpeed( x_i3, m_i1 )

        # construct spc initial velocity vectors
        spcdot_i3 = np.zeros( (3,3) )
        # assign random speed
        spcdot_i3[ : , 0 ] = fun.randomSpeed( escapeSpeed_i1 )[:,0]
        # assign angles
        for starIdx in [ 1, 2, 3 ]:
            for coordinateIdx in [ 1, 2 ]:
                colName = f"vel_({starIdx},{coordinateIdx},0)"
                if colName in inp.constantFactors:
                    spcdot_i3[ starIdx, coordinateIdx ] = inp.constantFactors[ colName ]
                elif colName in sampleRow:
                    spcdot_i3[ starIdx, coordinateIdx ] = sampleRow[ colName ]
                else:
                    self.__ColumnAssertion( colName )

        # calculate XYZ velocities
        xdot_i3 = fun.spc2xyz( spcdot_i3 )

        # find star radii
        r_i1 = fun.stellarRadiiLookup( m_i1 )

        # set starting run time and step counter
        steps, time = 0, 0

        # set terminition conditions
        collision = False
        ejection = False
        timeLimit = False

        # initialize time and positions to be updated
        x_i3_t    = deepcopy( x_i3 )
        xdot_i3_t = deepcopy( xdot_i3 )

        # initialize time step using smallest quotent of distance & initial
        # speed
        dt = fun.timeStep( x_i3, xdot_i3, initial=True, scale=inp.dt0ScaleFactor )

        # run scenario simulation----------------------------------------------#

        # run through simulation until any terminition conditions are met
        while not all([ collision, ejection, timeLimit ]):
            pdb.set_trace()
            # update time, time step, positions, and velocities
            time, dt, x_i3_t, xdot_i3_t = fun.nBodyRungeKutta4( time, dt, x_i3_t, xdot_i3_t, m_i1 )

            # see if any stars collided
            collision = fun.checkCollision( x_i3_t, r_i1 )

            # see if any stars are moving to fast
            ejection = fun.checkEjection( x_i3_t, xdot_i3_t, m_i1 )

            # see if timit limit has been exceeded
            timeLimit = ( time >= inp.maxT )

            # increment step counter
            steps += 1

            # convert ending values back to SPC
            spc_i3_t    = fun.xyz2spc( x_i3_t )
            spcdot_i3_t = fun.xyz2spc( xdot_i3_t )

        # collect results------------------------------------------------------#

        # collect results for ALL columns
        results = {
            'runTime'   : time,
            'collide'   : int( collision ),
            'eject'     : int( ejection ),
            'survive'   : int( timeLimit ),
            'nSteps'    : steps,
        }
        # add all final posigion and velocities
        for starIdx in [ 1, 2, 3 ]:
            for coordinateIdx in [ 0, 1, 2 ]:
                for name, array in zip(
                    [ 'pos'   , 'vel'      ],
                    [ spc_i3_t, spcdot_i3_t]
                ):
                    colName = f"{name}_({starIdx},{coordinateIdx},-1)"
                    results[ colName ] = array[ starIdx, coordinateIdx ]

        # update sample DataFrame----------------------------------------------#

        for colName, value in results.items():
            self.sample_.loc[ self.sampleRowIdx_, colName ] = value

        # end------------------------------------------------------------------#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def _getSample( self ):
        NotImplemented

    #===========================================================================#
    # semi-private                                                              #
    #===========================================================================#

    def __ColumnAssertion( self, colName ):
        raise AssertionError, f"can't seem to find {colName}! You \
        have to either include it in constant factors, control\
        factors, or random factors. If you want to include\
        any random factors, other than initial speed, you'll have to implement\
        it!"

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":
    sim = Simulation(
        nTreatments = 100
    )
    sim.run()
