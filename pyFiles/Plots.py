
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
from tqdm import tqdm

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
    size = 100**(r_i1[:,0] + 1)
    # print(size)

    # find CM
    CM = fun.findCM( x_i3, m_i3 )

    xmax = x_i3.max() * 1.1

    # make plot-----------------------------------------------------------------#

    fig = plt.figure( figsize=figsize )
    fig.suptitle( f"3D Positions for Sample {sampleRowIdx} and Time {timeIdx}", fontsize=fontsize+4 )

    ax = fig.add_subplot( 111, projection='3d' )
    ax.scatter( x_i3[:,0], x_i3[:,1], x_i3[:,2], c=c_i1[:,0], s=size, alpha=alpha, label='Star Positions' )
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

    earlyStop = kwargs['earlyStop'] if 'earlyStop' in kwargs else False

    sim = Simulation()

    def data_gen():

        # set terminition conditions
        collision = False
        ejection = False
        timeLimit = False

        valuesDict = sim.setupScenario(sampleRowIdx)
        dt = valuesDict['dt']
        maxT = inp.maxT
        time = 0
        while time < maxT:
        # for _ in tqdm(range(10)):

            valuesDict = sim.runScenario(valuesDict)
            collision = valuesDict['collide']
            ejection = valuesDict['eject']
            timeLimit = valuesDict['timeLimit']
            if earlyStop and any([collision, ejection, timeLimit]): break

            x_i3 = valuesDict['x_i3_t']
            m_i1 = valuesDict['m_i1']
            r_i1 = valuesDict['r_i1']
            c_i1 = fun.stellarColorLookup(m_i1)
            time = valuesDict['time']
            xmax = x_i3.max()*1.1
            yield x_i3, m_i1, r_i1, c_i1, time, xmax

    # create a figure with two subplots
    fig,ax = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True, figsize=(15,15))

    # collect lines and set up axies
    line = []
    for x in ax.flatten()[:-1]:
        l1, = (x.plot([], [], 'co', markersize=20)) # stars
        line.append(l1)

    def run( data ):

        # update the data
        x_i3, m_i1, r_i1, c_i1, time, xmax = data
        year = time / inp.yr2s

        # axis limits checking. Same as before, just for both axes
        for x, title, xIdx, yIdx, in zip(ax.flatten()[:-1], ['X-Y', 'X-Z', 'Y-Z'], [0,0,1], [1,2,2]):
            x.clear()
            x.set_aspect('equal')
            x.set_facecolor('k')
            x.set_title( title, fontsize=24)
            x.plot(x_i3[:,xIdx], x_i3[:,yIdx], 'co', markersize=20)
            x.set_xlim(-xmax, xmax)
            x.set_ylim(-xmax, xmax)
            x.plot([-xmax, xmax], [0, 0], 'w', lw=1, alpha=0.5)
            x.plot([0, 0], [-xmax, xmax], 'w', lw=1, alpha=0.5)
            x.annotate(
                f"year = {year:0.2f}",
                (-xmax*.9, xmax*.8),
                color = 'r',
                fontsize = 20
            )
            x.figure.canvas.draw()

        # update the data of both line objects
        # pdb.set_trace()
        # line[0].set_data(x_i3[:,0], x_i3[:,1])
        # line[1].set_data(x_i3[:,0], x_i3[:,2])
        # line[2].set_data(x_i3[:,1], x_i3[:,2])
        # for x in ax.flatten()[:-1]: x.figure.canvas.draw()

        # return line
        return line

    ani = animation.FuncAnimation(fig, run, data_gen, blit=True, interval=10, repeat=False)
    ani.save(f"figures/animation_{sampleRowIdx}.mp4", writer='ffmpeg')

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--sampleRowIdx', default=0)
    parser.add_argument('--timeIdx', default=0)
    parser.add_argument('--earlyStop', default=False)
    parser.add_argument('--show', default=True)
    parser.add_argument('--positionPlot', default=False)
    parser.add_argument('--animation', default=False)
    args = parser.parse_args()
    kwargs = args.__dict__

    # update key word arguments if presented
    for key in ['sampleRowIdx', 'timeIdx']: kwargs[key] = int(kwargs[key])
    for key in ['earlyStop', 'show', 'positionPlot', 'animation']:
        if any([kwargs[key]=="false", kwargs[key]=='False', kwargs[key]=='0']):
            kwargs[key] = False
        elif any([kwargs[key]=='true', kwargs[key]=='True', kwargs[key]=='1']):
            kwargs[key] = True

    if kwargs['positionPlot']: staticPositionPlot(**kwargs)
    if kwargs['animation']: scenarioAnimation(**kwargs)
