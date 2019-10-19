
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from BaseClass import BaseClass
from Input import radiusParams, thetaParams, phiParams, massParams, speedParams, maxT, G

import Functions as fun

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

    #===========================================================================#
    # semi-protected methods                                                    #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def _runScenario( self, **kwargs ):

        # scenario number
        n1 = self.sampleRowIdx_ + 1

        fun.printHeader(*[
            "",
            f"scenario:\t{n1} / {self.sample_.shape[0]}",
        ], verbose = True )

        # use the sampleRowIdx to get treatement values
        sampleRow = self.sample_.iloc[ self.sampleRowIdx_ ]

        # extract SPC positions from sampleRow
        spc_i3 = np.zeros( (3,3) )
        for starIdx in [ 0, 1, 2 ]:
            for colIdx, name in enumerate([ 'radius', 'theta', 'phi' ]):
                key = f"{name}_({starIdx},0)"
                spc_i3[ starIdx, colIdx ] = sampleRow[ key ]

        # extract masses from sampleRow
        m_i1 = np.array([ sampleRow[ f"mass_({starIdx})" ] for starIdx in range(3) ])[:,None]

        # calculate XYZ positions
        x_i3 = fun.spc2xyz( spc_i3, **kwargs )

        # calculate CM of the new system ( vector from current origin to CM )
        CM_13 = fun.findCM( x_i3, m_i1 )

        # make CM the new origin ( subtract CM vector from star positions )
        x_i3 -= CM_13

        # calculate escape velocity from system
        escapeSpeed_i1 = fun.escapeSpeed( x_i3, m_i1 )

        # create container to hold spc initial velocities
        spcdot_i3 = np.zeros( (3,3) )
        # assign random speed
        spcdot_i3[ : , 0 ] = fun.randomSpeed( escapeSpeed_i1 )[:,0]
        # fill in the polar and azimuthal angles
        for name, colIdx in zip(
            [ 'velTheta', 'velPhi' ],
            [ 1         , 2        ]
        ):
            for starIdx in [ 0, 1, 2 ]:
                key = f"{name}_({starIdx},0)"
                spcdot_i3[ starIdx, colIdx ] = sampleRow[ key ]

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

        # initialize time step using smallest quotent of distance/100 & initial
        # speed
        dt = fun.timeStep( x_i3, xdot_i3, initial=True, scale=1e-3 )

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
            timeLimit = ( time >= maxT )

            # increment step counter
            steps += 1

        # convert ending values back to SPC
        spc_i3_t    = fun.xyz2spc( x_i3_t )
        spcdot_i3_t = fun.xyz2spc( xdot_i3_t )

        # create empty container to hold scenario results
        results = {}

        # add the run time and misc columns
        results['runTime']   = time
        results['treatment'] = self.sampleRowIdx_
        results['replicate'] = self.replicateCounter_
        results['steps']     = steps
        if collision:
            results['outcome'] = 'collision'
        elif ejection:
            results['outcome'] = 'ejection'
        else:
            results['outcome'] = 'fullRun'

        # add all positions, velocities and mass for each star
        for starIdx in [ 0, 1, 2 ]:

            # add mass to results
            results[ f"mass_({starIdx})" ] = m_i1[ starIdx, 0 ]

            # add initial positions (SPC)
            for colIdx, name in enumerate([ 'radius', 'theta', 'phi' ]):
                results[ f"{name}_({starIdx},0)" ] = spc_i3[ starIdx, colIdx ]

            # add final positions( (SPC)
            for colIdx, name in enumerate([ 'radius', 'theta', 'phi' ]):
                results[ f"{name}_({starIdx},-1)" ] = spc_i3_t[ starIdx, colIdx ]

            # add initial velocities (SPC)
            for colIdx, name in enumerate([ 'velRadial', 'velPolar', 'velAzimuthal' ]):
                results[ f"{name}_({starIdx},0)" ] = spcdot_i3[ starIdx, colIdx ]

            # add final velocities (SPC)
            for colIdx, name in enumerate([ 'velRadial', 'velPolar', 'velAzimuthal' ]):
                results[ f"{name}_({starIdx},-1)" ] = spcdot_i3_t[ starIdx, colIdx ]

        # add the senario data to data_
        row = pd.DataFrame( results, index=[0] )
        self.data_ = self.data_.append( row, sort=False )

        # end

    #===========================================================================#
    # semi-private                                                              #
    #===========================================================================#

    def __generateConstantFactors( self ):

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


#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":
    sim = Simulation(
        nTreatments = 100
    )
    sim.run()
