
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
from tqdm import tqdm

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

        # only add sample DF if it doesn't already exist
        if not hasattr( self, 'sample_' ): self._getSample()

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
            self.runComplete_ = ( self.sampleRowIdx_ == self.sample_.shape[ 0 ] )
            # save current state of sim model
            self.saveState()
        self.sample_.to_csv( "data/Simulation.csv", index=False )

    #===========================================================================#
    # puplic methods                                                            #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

    def _runScenario( self, **kwargs ):

        # set terminition conditions
        collision = False
        ejection  = False
        timeLimit = False

        valuesDict = self.setupScenario( self.sampleRowIdx_ )
        dt   = valuesDict['dt']
        maxT = inp.maxT
        for _ in tqdm( range( int(maxT//dt) ) ):
            valuesDict  = self.runScenario( valuesDict )
            collision   = valuesDict['collision']
            ejection    = valuesDict['ejection']
            timeLimit   = valuesDict['timeLimit']
            if any([ collision, ejection, timeLimit ]): break
        self.recordScenario( valuesDict )

    #===========================================================================#
    # semi-protected methods                                                    #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def _getSample( self ):
        data = pd.read_csv( inp.sampleFileName )
        data.rename( columns=inp.sampleFileColumnMap, inplace=True )
        data.drop( columns=inp.sampleFileDropColumns, inplace=True )
        for colName in self.colNames_['all']:
            if not colName in data: data[colName] = np.nan
        self.sample_ = data

    #===========================================================================#
    # semi-private                                                              #
    #===========================================================================#

    def __columnAssertion( self, colName ):
        raise AssertionError(f"can't seem to find {colName}! You \
        have to either include it in constant factors, control\
        factors, or random factors. If you want to include\
        any random factors, other than initial speed, you'll have to implement\
        it!")

    def recordScenario( self, valuesDict ):
        vd = valuesDict

        # collect results for ALL columns
        results = {
            'runTime'   : vd['time'],
            'collide'   : int( vd['collision'] ),
            'eject'     : int( vd['ejection'] ),
            'survive'   : int( vd['timeLimit'] ),
            'nSteps'    : int( vd['steps'] ),
        }
        # add all final posigion and velocities
        for starIdx in range(3):
            for coordinateIdx in range(3):
                for name, array in zip(
                    [ 'pos'         , 'vel'             ],
                    [ vd['spc_i3_t'], vd['spcdot_i3_t'] ]
                ):
                    colName = f"{name}_({starIdx},{coordinateIdx},-1)"
                    results[ colName ] = array[ starIdx, coordinateIdx ]
        for colName, value in results.items():
            self.sample_.loc[ self.sampleRowIdx_, colName ] = value

    def runScenario( self, valuesDict ):
        vd = valuesDict

        # update time, time step, positions, and velocities
        vd['time'], vd['dt'], vd['x_i3_t'], vd['xdot_i3_t'] = fun.nBodyRungeKutta4( vd['time'], vd['dt'], vd['x_i3_t'], vd['xdot_i3_t'], vd['m_i1'] )

        # see if any stars collided
        vd['collision'] = fun.checkCollision( vd['x_i3_t'], vd['r_i1'] )

        # see if any stars are moving to fast
        vd['ejection'] = fun.checkEjection( vd['x_i3_t'], vd['xdot_i3_t'], vd['m_i1'] )

        # see if timit limit has been exceeded
        vd['timeLimit'] = ( vd['time'] >= inp.maxT )

        # increment step counter
        vd['steps'] += 1

        # convert ending values back to SPC
        vd['spc_i3_t']    = fun.xyz2spc( vd['x_i3_t'] )
        vd['spcdot_i3_t'] = fun.xyz2spc( vd['xdot_i3_t'] )

        # return the updated values dictionary
        return vd

    def setupScenario( self, sampleRowIdx ):

        # scenario number
        n1 = self.sampleRowIdx_ + 1

        fun.printHeader( f"scenario:\t{n1} / {self.sample_.shape[0]}", verbose = True )

        # use the sampleRowIdx to get treatement values
        sampleRow = self.sample_.iloc[ self.sampleRowIdx_ ]

        # construct SPC positions
        spc_i3 = np.zeros( (3,3) )
        for starIdx in range(3):
            for coordinateIdx in range(3):
                colName = f"pos_({starIdx},{coordinateIdx},0)"
                if colName in inp.constantFactors:
                    spc_i3[ starIdx, coordinateIdx ] = inp.constantFactors[ colName ]
                elif colName in sampleRow:
                    spc_i3[ starIdx, coordinateIdx ] = sampleRow[ colName ]
                else:
                    pdb.set_trace()
                    self.__columnAssertion( colName )
                self.sample_.loc[ self.sampleRowIdx_, colName ] = spc_i3[ starIdx, coordinateIdx ]

        # construct masses
        m_i1 = np.zeros( (3,1) )
        for starIdx in range(3):
            colName = f"mass_({starIdx})"
            if colName in inp.constantFactors:
                m_i1[ starIdx, 0 ] = inp.constantFactors[ colName ]
            elif colName in sampleRow:
                m_i1[ starIdx, 0 ] = sampleRow[ colName ]
            else:
                self.__columnAssertion( colName )

        # calculate XYZ positions
        x_i3 = fun.spc2xyz( spc_i3 )

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
        for starIdx in range(3):
            for coordinateIdx in [ 1, 2 ]:
                colName = f"vel_({starIdx},{coordinateIdx},0)"
                if colName in inp.constantFactors:
                    spcdot_i3[ starIdx, coordinateIdx ] = inp.constantFactors[ colName ]
                elif colName in sampleRow:
                    spcdot_i3[ starIdx, coordinateIdx ] = sampleRow[ colName ]
                else:
                    self.__columnAssertion( colName )

        # calculate XYZ velocities
        xdot_i3 = fun.spc2xyz( spcdot_i3 )

        # find star radii
        r_i1 = fun.stellarRadiiLookup( m_i1 )

        # set starting run time and step counter
        steps, time = 0, 0

        # initialize time and positions to be updated
        x_i3_t    = deepcopy( x_i3 )
        xdot_i3_t = deepcopy( xdot_i3 )

        # initialize time step using smallest quotent of distance & initial
        # speed
        # dt = fun.timeStep( x_i3, xdot_i3, initial=True, scale=inp.dt0ScaleFactor )
        dt = 60*60*24

        # return all the locally defined variables as dictionary
        return locals()

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
