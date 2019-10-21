
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
import Input as inp
from Simulation import Simulation

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D
import matplotlib.animation as animation
import numpy as np
import pdb
import tqdm

#===============================================================================#
# static 3D plot of positions                                                   #
#===============================================================================#

def staticPositionPlot( sampleRowIdx=0, timeIdx=0, **kwargs ):

    # set variables with key words
    alpha = kwargs['alpha'] if 'alpha' in kwargs else 1
    figsize = kwargs['figsize'] if 'figsize' in kwargs else (15,15)
    fontsize = kwargs['fontsize'] if 'fontsize' in kwargs else 20
    save = kwargs['save'] if 'save' in kwargs else True
    show = kwargs['show'] if 'show' in kwargs else (not save)
    toFile = kwargs['toFile'] if 'toFile' in kwargs else f"static3D_{sampleRowIdx}_{timeIdx}"

    # collect data--------------------------------------------------------------#

    # grab sim state
    simState = fun.fromPickle( 'Simulation' )
    if len( simState ) == 0:
        fun.printHeader( "sim hasn't run yet, try running sim first" )
        return

    # grab scenario from sample data
    scenario = simState[ 'sample_' ].iloc[ sampleRowIdx ]

    # construct SPC positions
    spc_i3 = np.zeros( (3,3) )
    for starIdx in range(3):
        for coordinateIdx in range(3):
            colName = f"pos_({starIdx},{coordinateIdx},{timeIdx})"
            spc_i3[ starIdx, coordinateIdx ] = scenario[ colName ]

    # convert to XYZ coordinates
    x_i3 = fun.spc2xyz( spc_i3 )

    # construct mass
    m_i3 = np.zeros( (3,1) )
    for starIdx in range(3):
        colName = f"mass_({starIdx})"
        m_i3[ starIdx ] = scenario[ colName ]

    # look up radii and colors
    r_i1 = fun.stellarRadiiLookup( m_i3 )
    c_i1 = fun.stellarColorLookup( m_i3 )

    # find CM
    CM = fun.findCM( x_i3, m_i3 )

    xmax = x_i3.max() * 1.1

    # make plot-----------------------------------------------------------------#

    fig = plt.figure( figsize=figsize )
    fig.suptitle( f"3D Positions for Sample {sampleRowIdx} and Time {timeIdx}", fontsize=fontsize+4 )

    ax = fig.add_subplot( 111, projection='3d' )
    ax.scatter( x_i3[:,0], x_i3[:,1], x_i3[:,2], c=c_i1[:,0], s=1e9*r_i1[:,0], alpha=alpha, label='Star Positions' )
    ax.plot( CM[:,0], CM[:,1], CM[:,2], color='#EC13E2', marker='X', markersize=12, label='Center of Mass' )
    ax.plot( [-xmax,xmax],[0,0],[0,0], 'c', linewidth=3, label='x' )
    ax.plot( [0,0],[-xmax,xmax],[0,0], 'g', linewidth=3, label='y' )
    ax.plot( [0,0],[0,0],[-xmax,xmax], 'b', linewidth=3, label='z' )
    # ax.set_aspect( 'equal' )
    ax.auto_scale_xyz([-xmax,xmax], [-xmax,xmax], [-xmax,xmax])
    ax.set_facecolor( 'k' )
    ax.set_xlabel("X [ly]", fontsize=fontsize )
    ax.set_ylabel("Y [ly]", fontsize=fontsize )
    ax.set_zlabel("Z [ly]", fontsize=fontsize )
    ax.legend( loc='best', fontsize=fontsize )

    # save/close----------------------------------------------------------------#

    if show: plt.show()
    if save: fun.saveFigure( toFile, fig )
    plt.close( fig )

#===============================================================================#
# example animation of scenario                                                 #
#===============================================================================#

def scenarioAnimation( sampleRowIdx=0, timeIdx=0, **kwargs ):
    """
    https://matplotlib.org/3.1.1/api/animation_api.html
    https://towardsdatascience.com/animations-with-matplotlib-d96375c5442c
    https://matplotlib.org/gallery/animation/subplots.html
    https://stackoverflow.com/a/29834816/6943976
    """
    sim = Simulation()

    def data_gen():

        # set terminition conditions
        collision = False
        ejection  = False
        timeLimit = False

        valuesDict = sim.setupScenario( sampleRowIdx )
        dt   = valuesDict['dt']
        maxT = inp.maxT
        for _ in tqdm( range( 10 ) ):

            valuesDict  = self.runScenario( valuesDict )
            collision   = valuesDict['collision']
            ejection    = valuesDict['ejection']
            timeLimit   = valuesDict['timeLimit']
            if any([ collision, ejection, timeLimit ]): break

            runTime = valuesDict['runTime']
            x_i3    = valuesDict['x_i3_t']
            m_i1    = valuesDict['m_i1']
            r_i1    = valuesDict['r_i1']
            c_i1    = fun.stellarColorLookup( m_i1 )
            xmax    = x_i3.max()*1.1
            yield runTime, x_i3, m_i1, r_i1, c_i1, xmax

    # create a figure with two subplots
    fig,ax = plt.subplots( nrows=2, ncols=2, sharex=True, sharey=True, figsize=(15,15) )

    # collect lines and set up axies
    line = []
    for x in ax.flatten()[:-1]:
        line.append( x.scatter( [], [], c=[], s=[] ) ) # stars
        line.append( x.vlines( 0, [], [], 'k', lw=3 ) ) # subplot x-axis
        line.append( x.hlines( 0, [], [], 'k', lw=3 ) ) # subplot y-axis
        x.grid()
    for x in ax.flatten():
        x.set_aspect( 'equal' )
        x.set_facecolor( 'k' )
    plt.tight_layout()

    def run( data ):

        # update the data
        runTime, x_i3, m_i1, r_i1, c_i1, xmax = data

        # axis limits checking. Same as before, just for both axes
        for i, x in enumerate( ax.flatten()[:-1] ):
            x.set_xlim( -xmax, xmax )
            x.set_ylim( -xmax, xmax )
            x.figure.canvas.draw()

        # update the data of both line objects
        line[0].set_data( x_i3[:,0], x_i3[:,1], c_i1[:,0], 1e9*r_i1[:,0] )
        line[1].set_data( xmax, xmax )
        line[2].set_data( xmax, xmax )
        line[3].set_data( x_i3[:,0], x_i3[:,2], c_i1[:,0], 1e9*r_i1[:,0] )
        line[4].set_data( xmax, xmax )
        line[5].set_data( xmax, xmax )
        line[6].set_data( x_i3[:,1], x_i3[:,2], c_i1[:,0], 1e9*r_i1[:,0] )
        line[7].set_data( xmax, xmax )
        line[8].set_data( xmax, xmax )

        return line

    ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=10, repeat=False)
    plt.show()

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--sampleRowIdx')
    parser.add_argument('--timeIdx')
    parser.add_argument('--show')
    args = parser.parse_args()

    # set default key words
    kwargs = {
        'sampleRowIdx'  : 0,
        'timeIdx'       : 0,
        'show'          : False,
    }

    # update key word arguments if presented
    if args.sampleRowIdx != None: kwargs['sampleRowIdx'] = int( args.sampleRowIdx )
    if args.timeIdx != None: kwargs['timeIdx'] = int( args.sample )

    # staticPositionPlot( **kwargs )
    ani = scenarioAnimation()
