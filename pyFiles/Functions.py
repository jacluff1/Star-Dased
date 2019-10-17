def generic():
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

#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from Input import G, radiusParams, speedParams, thetaParams, phiParams, massParams
import Input

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import pickle
import warnings

#===============================================================================#
# auxillary                                                                     #
#===============================================================================#

def findIdx( value, array ):
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
    idx = np.abs( array - value ).argmin()
    return idx

def stellarRadiiLookup( m_i1 ):

    # load stellar data to pd.DataFrame
    table = pd.read_csv( "data/starClass.txt" )

    # pull mass and radius columns from table, reversing order to be in
    # numerical order.
    mass  = table.mass.values[::-1]
    radii = table.radius.values[::-1]

    # allowable mass values
    mass1 = np.linspace( *massParams )

    # interpolate lower resolution table values
    radii1 = np.interp( mass1, mass, radii )

    # create empty stellar radius array
    radius = np.zeros((
        m_i1.shape[0], # number of bodies
        1
    ))

    for starIdx, starMass in enumerate( m_i1 ):
        # find the radius index by looking up the mass index
        idx = findIdx( starMass, mass1 )
        # fill in the star radius
        radius[ starIdx, 0 ] = radii1[ idx ]

    return radius

#===============================================================================#
# coordinate frames                                                             #
#===============================================================================#

def findCM( x_i3, m_i1, **kwargs ):
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
    CM = ( m_i1 * x_i3 ).sum( axis=0 ) / m_i1.sum()
    return CM[None,:]

def spc2xyz( spc_i3, **kwargs ):

    r = spc_i3[:,0]

    sinTheta = np.sin( spc_i3[:,1] )
    cosTheta = np.cos( spc_i3[:,1] )

    sinPhi = np.sin( spc_i3[:,2] )
    cosPhi = np.cos( spc_i3[:,2] )

    x_i3 = np.zeros( spc_i3.shape )

    x_i3[:,0] = r * sinTheta * cosPhi
    x_i3[:,1] = r * sinTheta * sinPhi
    x_i3[:,2] = r * cosTheta

    return x_i3

def xyz2spc( x_i3, **kwargs ):

    r   = np.sqrt( ( x_i3**2 ).sum( axis=1 ) )
    rho = np.sqrt( ( x_i3[:,:2]**2 ).sum( axis=1 ) )

    spc = np.zeros( x_i3.shape )

    spc[:,0] = r
    spc[:,1] = np.arctan( rho / x_i3[:,2] )
    spc[:,2] = np.arctan( x_i3[:,1] / x_i3[:,0] )

    return spc

#===============================================================================#
# file handling                                                                 #
#===============================================================================#

def toPickle( toFile, fromObject, **kwargs ):
    """
    use:
    sends object (preferably dictionary) to pickle and saves at file name
    provided.
    https://pythonprogramming.net/python-pickle-module-save-objects-serialization/

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    toFile          str             file name to save at
    fromObject      dict            dictionary (or other object) to send to
                                    pickle.

    kwargs:         type:           description:
    verbose         bool            whether to print save message.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    if os.path.isdir( "data" ):
        toFile = f"data/{toFile}.pkl"
    elif os.path.isdir( "../data" ):
        toFile = f"../data/{toFile}.pkl"

    pickle.dump(
        fromObject,             # object to write
        open( toFile, "wb" )    # open file and write object to it in bytes
    )

    printHeader( f"\n\tsaved pickle to {toFile}", **kwargs )

def fromPickle( fromFile, **kwargs ):
    """
    use:
    loads object (preferably from dictionary) from file name provided. if not
    file found, returns empty dictionary.
    https://pythonprogramming.net/python-pickle-module-save-objects-serialization/

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    fromFile        str             file name to look for pickled object

    kwargs:         type:           description:
    verbose         bool            whether to print load message.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    toObject        dict (or other object)
    """

    if os.path.isfile( f"data/{fromFile}.pkl" ):
        fromFile = f"data/{fromFile}.pkl"
    elif os.path.isfile( f"../data/{fromFile}.pkl" ):
        fromFile = f"../data/{fromFile}.pkl"
    else:
        return {}

    toObject = pickle.load(
        open( fromFile, 'rb' ) # read the byte file
    )

    return toObject

def saveFigure( toFile, fig, **kwargs ):
    """
    use:
    save a figure, print save destination if verbose

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    toFile          str             file name to save figure
    fig             matplotlib.figure

    kwargs:         type:           description:
    verbose         bool            flag to print, default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """
    toFile = f"../figures/{toFile}.pdf"
    fig.savefig( toFile )
    plt.close( fig )
    printHeader( f"\n\tsaved figure: {toFile}", **kwargs )

#===============================================================================#
# math & physics                                                                #
#===============================================================================#

def escapeSpeed( x_i3, m_i1 ):

    warnings.filterwarnings("ignore", message="divide by zero encountered in true_divide" )

    # find the pair-wise distances
    x_ij = pairwiseDistance( x_i3 )

    # calculate intermidiary result
    alpha_ij = m_i1 / x_ij + m_i1.T / x_ij
    np.nan_to_num( alpha_ij, posinf=0, copy=False )

    # sum up all ( mass : distance ) contributions along axis = 1 = j,
    # "from body"
    alpha_i1 = alpha_ij.sum( axis=1, keepdims=True )

    # calculate escape speed for all stars, converting so (km/2) comes out
    speed_i1 = np.sqrt( 2 * G * alpha_i1 / Input.km2ly )

    return speed_i1

def nBodyAcceleration( x_i3, m_i1, **kwargs ):
    """
    ( i , j , 3 )
    i --> on body
    j --> from body
    3 --> xyz spatial vector
    """

    # find pair-wise difference vectors
    x_ij3 = pairwiseDifferenceVector( x_i3, **kwargs )

    # find pair-wise distances
    x_ij = pairwiseDistance( x_ij3 )
    x_ij[ x_ij == 0 ] = 1

    # find pair-wise force directions
    hat_ij3 = x_ij3 / x_ij[:,:,None]
    # np.nan_to_num( hat_ij3, copy=False )

    # find pair-wise mass product
    m_ij = m_i1 * m_i1.T

    # find piece-wise force of gravity
    f_ij3 = hat_ij3 * G * m_ij[:,:,None] / x_ij[:,:,None]**2

    # sum up forces along ( 1 - from body ) to get forces on bodies
    f_i3 = f_ij3.sum( axis=1 )

    # get acellerations on bodies
    a_i3 = f_i3 / m_i1
    return a_i3

def pairwiseDifferenceVector( x_i3, **kwargs ):
    x_ij3 = x_i3 - x_i3[:,None,:]
    return x_ij3

def pairwiseDistance( x, **kwargs ):

    # determine if x is of form x_ij3
    if len( x.shape ) == 3:
        x_ij3 = x
    # or if x is of form x_i3
    elif len( x.shape ) == 2:
        x_ij3 = pairwiseDifferenceVector( x )

    # use he pairwise difference vectors to find pairwise distance ( sum along
    # spacial dimention )
    x_ij = np.sqrt( ( x_ij3**2 ).sum( axis=2 ) )
    return x_ij

def RungeKutta4( f, dt, x, *args ):

    k1  = f( x, *args )
    k23 = f( x + dt/2, *args )
    k4  = f( x + dt, *args )

    delta_y = dt * ( k1 + 2*k23 + 2*k23 + k4 ) / 6
    return delta_y

def timeStep( x_i3, xdot_i3, **kwargs ):

    initial = kwargs['initial'] if 'initial' in kwargs else False

    if initial:
        # if finding initial time step, x_i3 is position vectors;
        # find the magnitudes and divide by 100
        dx_i1 = np.sqrt( ( x_i3**2 ).sum( axis=1, keepdims=True ) ) / 100.0
    else:
        # if executed during while loop, x_i3 is dx_i3; just find the magnitudes
        dx_i1 = np.sqrt( ( x_i3**2 ).sum( axis=1, keepdims=True ) )

    # convert dx_i1 from ly --> km
    dx_i1 /= Input.km2ly

    # find the speeds
    dspeed_i1 = np.sqrt( ( xdot_i3**2 ).sum( axis=1, keepdims=True ) )
    # calulate time step, take the minimum quotient
    delta_t = ( dx_i1 / dspeed_i1 ).min()
    return delta_t

#===============================================================================#
# printing                                                                      #
#===============================================================================#

def printBreak( **kwargs ):
    """
    use:
    prints a decorated break in terminal

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:

    kwargs:         type:           description:
    verbose         bool            whether to actually print or not.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    verbose = kwargs['verbose'] if 'verbose' in kwargs else False

    if verbose: print("\n\
        ========================================================================\
    ")

def printDict( dictionary, **kwargs ):
    """
    use:
    prints dictionary in a decorated and readable format

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    dictionary      dict            a dictionary to print

    kwargs:         type:           description:
    message         str             message to print in header, default =
                                    "dictionary"
    verbose         bool            whether to actually print or not.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    message = kwargs['message'] if 'message' in kwargs else "dictionary"
    verbose = kwargs['verbose'] if 'verbose' in kwargs else False

    if verbose:

        # package dictionary
        lines = [ "", f"{message}", "key:\tvalue", "=============" ]
        for key,value in dictionary.items():
            try:
                lines.append( f"{key}:\t{value:0.2f}" )
            except:
                lines.append( f"{key}:\t{value}" )
        printHeader( *lines, **kwargs )

def printHeader( *args, **kwargs ):
    """
    use:
    prints a decorated section header with any optional provided arguments
    printed on a new line.

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    line(s)         str             each provided argument gets printed in the
                                    header on a new line

    kwargs:         type:           description:
    verbose         bool            whether to actually print or not.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None
    """

    verbose = kwargs['verbose'] if 'verbose' in kwargs else False

    if verbose:
        printBreak( **kwargs )
        for arg in args:
            try:
                print( f"\t{arg:0.2f}" )
            except:
                print( f"\t{arg}" )
        printBreak( **kwargs )

def printList( list1, **kwargs ):
    """
    use:

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:

    kwargs:         type:           description:
    message         str             message to print in header, default =
                                    "List"
    verbose         bool            whether to actually print or not.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    message = kwargs['message'] if 'message' in kwargs else "List"
    verbose = kwargs['verbose'] if 'verbose' in kwargs else False

    if verbose:

        # package dictionary
        lines =  [ "", f"{message}", "=============" ]
        lines += list1
        printHeader( *lines, **kwargs )

#===============================================================================#
# random generator                                                              #
#===============================================================================#

def randomSpeed( maxSpeed_i1 ):

    # make empty array with same shape as input
    spcdot_i3 = np.zeros( maxSpeed_i1.shape )

    # fill in random angles
    for starIdx, maxSpeed in enumerate( maxSpeed_i1 ):

        # construct speed args
        speedArgs = (
            speedParams[0], # min speed
            maxSpeed.item(), # max speed
            speedParams[1], # number of allowed values
        )

        # construct allowable speed value
        speed = np.linspace( *speedArgs )

        # select random index
        randIdx = np.random.randint( speedArgs[2] )

        # fill in random radial value and dicrection
        try:
            spcdot_i3[ starIdx, 0] = speed[ randIdx ]
        except:
            pdb.set_trace()

    return spcdot_i3

#===============================================================================#
# termination conditions                                                        #
#===============================================================================#

def checkCollision( x_i3, r_i1 ):

    # find the pair-wise distance for each body
    x_ij = pairwiseDistance( x_i3 )

    # find the pair-wise sum of radii
    r_ij = r_i1 + r_i1.T
    # convert diagonal to 0, since these pairs are not viable sim pairs
    np.fill_diagonal( r_ij, 0 )

    # determine any collitions
    collisions = ( r_ij > x_ij )
    return np.any( collisions )

def checkEjection( xdot_i3, x_i3, m_i1 ):

    # determine the escape velocity from the system for each body
    maxSpeed = escapeSpeed( x_i3, m_i1 )

    # calculate the speed of each body
    speed = np.sqrt( ( xdot_i3**2 ).sum( axis=1, keepdims=True ) )

    pdb.set_trace()
    # determine any eminent ejections
    ejections = ( speed > maxSpeed )
    return np.any( ejections )
