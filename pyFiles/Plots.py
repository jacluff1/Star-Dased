
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import numpy as np

#===============================================================================#
# static 3D plot of positions                                                   #
#===============================================================================#

def staticPositionPlot( sampleRowIdx=0, timeIdx=0, **kwargs ):

    # set variables with key words
    alpha = kwargs.pop('alpha') if 'alpha' in kwargs else 0.8
    figsize = kwargs.pop('figsize') if 'figsize' in kwargs else (15,15)
    fontsize = kwargs.pop('fontsize') if 'fontsize' in kwargs else 20
    save = kwargs.pop('save') if 'save' in kwargs else True
    show = kwargs.pop('show') if 'show' in kwargs else (not save)
    toFile = kwargs.pop('toFile') if 'toFile' in kwargs else f"static3D_{sampleRowIdx}_{timeIdx}.pdf"

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
    for starIdx in [ 1, 2, 3 ]:
        for coordinateIdx in [ 0, 1, 2 ]:
            colName = f"pos_({starIdx},{coordinateIdx},{timeIdx})"
            spc_i3[ starIdx, coordinateIdx ] = scenario[ colName ]

    # convert to XYZ coordinates
    x_i3 = fun.spc2xyz( spc_i3 )

    # construct mass
    m_i3 = np.zeros( (3,1) )
    for starIdx in [ 1, 2, 3 ]::
        colName = f"mass_({starIdx})"
        m_i3[ starIdx ] = scenario[ colName ]

    # look up radii and colors
    r_i1 = fun.stellarRadiiLookup( m_i3 )
    c_i1 = fun.stellarColorLookup( m_i3 )

    # find CM
    CM = fun.findCM( x_i3, m_i3 )

    # make plot-----------------------------------------------------------------#

    fig = plt.figure( figsize=figsize )
    fig.suptitle( f"3D Positions for Sample {sampleRowIdx} and Time {timeIdx}", fontsize=fontsize+4 )

    ax = fig.add_subplot( 111, projection='3d' )
    ax.scatter( x_i3[:,0], x_i3[:,1], x_i3[:,2], c=c_i1[:,0], s=r_i1[:,0], alpha=alpha, label='Star Positions' )
    ax.plot( CM[:,0], CM[:,1], CM[:,2], color='#EC13E2', marker='X', markersize=12, label='Center of Mass' )
    ax.set_aspect( 1 )
    ax.set_facecolor( 'k' )
    ax.set_xlabel("X [ly]", fontsize=fontsize )
    ax.set_ylabel("Y [ly]", fontsize=fontsize )
    ax.set_zlabel("Z [ly]", fontsize=fontsize )
    ax.legend( loc='best', fontsize=fontsize )

    # save/close----------------------------------------------------------------#

    if show: plt.show()
    if save: fig.savefig( toFile )
    plt.close( fig )

#===============================================================================#
# example animation of scenario                                                 #
#===============================================================================#

https://matplotlib.org/3.1.1/api/animation_api.html
