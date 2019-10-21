
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
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

    def data_gen():
        t = data_gen.t
        cnt = 0
        while cnt < 1000:
            cnt+=1
            t += 0.05
            y1 = np.sin(2*np.pi*t) * np.exp(-t/10.)
            y2 = np.cos(2*np.pi*t) * np.exp(-t/10.)
            # adapted the data generator to yield both sin and cos
            yield t, y1, y2

    data_gen.t = 0

    # create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2,1)

    # intialize two line objects (one in each axes)
    line1, = ax1.plot([], [], lw=2)
    line2, = ax2.plot([], [], lw=2, color='r')
    line = [line1, line2]

    # the same axes initalizations as before (just now we do it for both of them)
    for ax in [ax1, ax2]:
        ax.set_ylim(-1.1, 1.1)
        ax.set_xlim(0, 5)
        ax.grid()

    # initialize the data arrays
    xdata, y1data, y2data = [], [], []
    def run(data):
        # update the data
        t, y1, y2 = data
        xdata.append(t)
        y1data.append(y1)
        y2data.append(y2)

        # axis limits checking. Same as before, just for both axes
        for ax in [ax1, ax2]:
            xmin, xmax = ax.get_xlim()
            if t >= xmax:
                ax.set_xlim(xmin, 2*xmax)
                ax.figure.canvas.draw()

        # update the data of both line objects
        line[0].set_data(xdata, y1data)
        line[1].set_data(xdata, y2data)

        return line

    ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=10,
        repeat=False)
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
    # animation( **kwargs )
    ani = scenarioAnimation()
    # ani.save('test_sub.mp4')
    plt.show()
