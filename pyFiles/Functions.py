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

import Input as inp

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

def findIdx(value, array):
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

def stellarColorLookup(m_i1):

    # load stellar data to pd.DataFrame
    table = pd.read_csv( "data/starClass.txt" )

    # construct empty colors
    c_i1 = np.empty( (3,1), dtype='U8')

    for massIdx, mass in enumerate( m_i1 ):
        # find rowIdx that matches closest with mass
        rowIdx = findIdx( mass.item(), table.mass.values )
        c_i1[ massIdx, 0 ] = table.loc[ rowIdx, 'color' ]

    return c_i1

def stellarRadiiLookup(m_i1):

    # load stellar data to pd.DataFrame
    table = pd.read_csv( "data/starClass.txt" )

    # pull mass and radius columns from table, reversing order to be in
    # numerical order.
    mass   = table.mass.values[::-1] # solar mass
    radii  = table.radius.values[::-1] # solar radii
    radii *= inp.sr2ly # ly

    # generate a range of masses
    mass1 = np.linspace(
        mass.min(), # minimum mass allowed (solar mass)
        mass.max(), # maximum mass allowed (solar mass)
        inp.randomFactorParams[1], # number of masses
    )

    # interpolate lower resolution table values
    radii1 = np.interp( mass1, mass, radii ) # ly

    # create empty stellar radius array
    r_i1 = np.zeros( m_i1.shape ) # ly

    for starIdx, starMass in enumerate( m_i1 ):
        # find the radius index by looking up the mass index
        idx = findIdx( starMass, mass1 ) # int
        # fill in the star radius
        r_i1[ starIdx, 0 ] = radii1[ idx ] # ly

    return r_i1 # ly

#===============================================================================#
# coordinate frames                                                             #
#===============================================================================#

def findCM(x_i3, m_i1, **kwargs):
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
    CM = ( m_i1 * x_i3 ).sum( axis=0 ) / m_i1.sum() # ly
    return CM[None,:] # ly

def spc2xyz(spc_i3, **kwargs):

    r = spc_i3[:,0] # ly

    sinTheta = np.sin( spc_i3[:,1] ) # float
    cosTheta = np.cos( spc_i3[:,1] ) # float

    sinPhi = np.sin( spc_i3[:,2] ) # float
    cosPhi = np.cos( spc_i3[:,2] ) # float

    x_i3 = np.zeros( spc_i3.shape ) # ly

    x_i3[:,0] = r * sinTheta * cosPhi # ly
    x_i3[:,1] = r * sinTheta * sinPhi # ly
    x_i3[:,2] = r * cosTheta # ly

    return x_i3 # ly

def xyz2spc(x_i3, **kwargs):

    r   = np.sqrt( ( x_i3**2 ).sum( axis=1 ) ) # ly
    rho = np.sqrt( ( x_i3[:,:2]**2 ).sum( axis=1 ) ) # ly

    spc = np.zeros( x_i3.shape ) # ly

    spc[:,0] = r # ly
    spc[:,1] = np.arctan( rho / x_i3[:,2] ) # radians
    spc[:,2] = np.arctan( x_i3[:,1] / x_i3[:,0] ) # radians

    return spc # [ ly, radians, radians ]

#===============================================================================#
# file handling                                                                 #
#===============================================================================#

def fromPickle(fromFile, **kwargs):
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
    elif os.path.isfile( fromFile ):
        fromFile = fromFile
    else:
        return {}

    toObject = pickle.load(
    open( fromFile, 'rb' ) # read the byte file
    )

    return toObject

def toPickle(toFile, fromObject, **kwargs):
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
    # toFile
    #
    # if os.path.isdir( "data" ):
    #     toFile = f"data/{toFile}.pkl"
    # elif os.path.isdir( "../data" ):
    #     toFile = f"../data/{toFile}.pkl"
    # else:
    #     pdb.set_trace()

    pickle.dump(
        fromObject,             # object to write
        open( toFile, "wb" )    # open file and write object to it in bytes
    )

    printHeader( f"saved pickle to {toFile}", **kwargs )

def saveFigure(toFile, fig, **kwargs):
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
    toFile = f"figures/{toFile}.pdf"
    fig.savefig( toFile )
    plt.close( fig )
    printHeader( f"saved figure: {toFile}", **kwargs )

#===============================================================================#
# math & physics                                                                #
#===============================================================================#

def escapeSpeed(x_i3, m_i1):

    warnings.filterwarnings("ignore", message="divide by zero encountered in true_divide" )

    # find the pair-wise distances
    x_ij = pairwiseDistance( x_i3 ) # ly

    # calculate intermidiary result
    alpha_ij = m_i1 / x_ij + m_i1.T / x_ij # solar mass ly^-1
    np.nan_to_num( alpha_ij, posinf=0, copy=False )

    # sum up all ( mass : distance ) contributions along axis = 1 = j,
    # "from body"
    alpha_i1 = alpha_ij.sum( axis=1, keepdims=True ) # solar mass ly^-1

    # calculate escape speed for all stars, converting so (km/2) comes out
    speed_i1 = np.sqrt( 2 * inp.G * alpha_i1 ) # km/s

    return speed_i1 # km/s

def nBodyAcceleration(x_i3, m_i1):
    """
    ( i , j , 3 )
    i --> on body
    j --> from body
    3 --> xyz spatial vector
    """

    # find pair-wise difference vectors
    x_ij3 = pairwiseDifferenceVector( x_i3 ) # ly

    # find pair-wise distances
    x_ij = pairwiseDistance( x_ij3 ) # ly
    x_ij[ x_ij == 0 ] = 1

    # find pair-wise force directions
    hat_ij3 = x_ij3 / x_ij[:,:,None]

    # find pair-wise mass product
    m_ij = m_i1 * m_i1.T # (solar mass)^2

    # find piece-wise force of gravity
    f_ij3  = hat_ij3 * inp.G * m_ij[:,:,None] / x_ij[:,:,None]**2 # (solar mass) (km/s)^2 (ly)^-1
    f_ij3 *= inp.km2ly # (solar mass) (km/s^2)

    # sum up forces along ( 1 - from body ) to get forces on bodies
    f_i3 = f_ij3.sum( axis=1 ) # (solar mass) (km/s^2)

    # get acellerations on bodies
    a_i3 = f_i3 / m_i1 # km/s^2
    return a_i3 # km/s^2

def pairwiseDifferenceVector(x_i3):
    x_ij3 = x_i3 - x_i3[:,None,:] # ly
    return x_ij3 # ly

def pairwiseDistance(x):

    # determine if x is of form x_ij3
    if len( x.shape ) == 3:
        x_ij3 = x # ly
    # or if x is of form x_i3
    elif len( x.shape ) == 2:
        x_ij3 = pairwiseDifferenceVector( x ) # ly

    # use he pairwise difference vectors to find pairwise distance ( sum along
    # spacial dimention )
    x_ij = np.sqrt( ( x_ij3**2 ).sum( axis=2 ) ) # ly
    return x_ij # ly

def nBodyRungeKutta4(time, dt, x_i3, xdot_i3, m_i1):
    """
    http://spiff.rit.edu/richmond/nbody/OrbitRungeKutta4.pdf
    """

    # find coefficients for RK4
    kr1  = xdot_i3 # km/s
    # kr1 *= inp.km2ly # ly/s
    kv1  = nBodyAcceleration(x_i3, m_i1) # km/s^2

    kr2  = xdot_i3 * kv1 * dt/2 # km/s
    # kr2 *= inp.km2ly # ly/s
    kv2  = nBodyAcceleration(x_i3 + kr1 * dt/2, m_i1) # km/s^2

    kr3  = xdot_i3 * kv2 * dt/2 # km/s
    # kr3 *= inp.km2ly # ly/s
    kv3  = nBodyAcceleration(x_i3 + kr2 * dt/2, m_i1) # km/s^2

    kr4  = xdot_i3 * kv3 * dt # km/s
    # kr4 *= inp.km2ly # ly/s
    kv4  = nBodyAcceleration(x_i3 + kr3 * dt/2, m_i1) # km/s^2

    # update positions and velocities
    dx_i3 = (dt/6) * (kr1 + 2*kr2 + 2*kr3 + kr4) # ly
    dv_i3 = (dt/6) * (kv1 + 2*kv2 + 2*kv3 + kv4) # km/s^2

    # dv_i3 = nBodyAcceleration(x_i3, m_i1)
    # dx_i3 = dv_i3*dt

    # update positions and velocities
    x_i3 += dx_i3
    xdot_i3 += dv_i3

    # shift positions relative to CM
    CM_13 = findCM( x_i3, m_i1 ) # ly
    x_i3 -= CM_13 # ly

    # update time
    time += dt # s

    # update time-step
    dt = timeStep( x_i3, xdot_i3 ) # s
    pdb.set_trace()
    # output time, time-step, positions, and velocities
    return time, dt, x_i3, xdot_i3 # s, s, ly, km/s

def timeStep(x_i3, xdot_i3, **kwargs):

    initial = kwargs['initial'] if 'initial' in kwargs else False
    scale = kwargs['scale'] if 'scale' in kwargs else 1e-8

    # if finding initial time step, x_i3 is position vectors
    dx_i1 = np.sqrt( ( x_i3**2 ).sum( axis=1, keepdims=True ) ) # ly

    if initial:
        # find the magnitudes and divide by 100
        dx_i1 = np.sqrt( ( x_i3**2 ).sum( axis=1, keepdims=True ) ) * scale # ly

    # convert dx_i1 from ly --> km
    dx_i1 /= inp.km2ly # km

    # find the speeds
    xdot_i1 = np.sqrt( ( xdot_i3**2 ).sum( axis=1, keepdims=True ) ) # km/s
    # calulate time step, take the minimum quotient
    delta_t = ( dx_i1 / xdot_i1 ).min() # s
    return delta_t # s

#===============================================================================#
# printing                                                                      #
#===============================================================================#

def printBreak(**kwargs):
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
    \n")

def printDict(dictionary, **kwargs):
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
        lines = [ f"{message}", "key:\tvalue", "=============" ]
        for key,value in dictionary.items():
            try:
                lines.append( f"{key}:\t{value:0.2f}" )
            except:
                lines.append( f"{key}:\t{value}" )
        printHeader( *lines, **kwargs )

def printHeader(*args, **kwargs):
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

def printList(list1, **kwargs):
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
        lines =  [ f"{message}", "=============" ]
        lines += list1
        printHeader( *lines, **kwargs )

#===============================================================================#
# random generator                                                              #
#===============================================================================#

def randomSpeed(maxSpeed_i1):

    # make empty array with same shape as input
    spcdot_i3 = np.zeros( maxSpeed_i1.shape ) # km/s

    # fill in random angles
    for starIdx, maxSpeed in enumerate( maxSpeed_i1 ):

        # construct speed args
        speedArgs = (
            inp.randomFactorParams[0], # min speed (km/s)
            maxSpeed.item(), # max speed (km/s)
            inp.randomFactorParams[1], # number of allowed values (int)
        )

        # construct allowable speed value
        speed = np.linspace( *speedArgs ) # km/s

        # select random index
        randIdx = np.random.randint( speedArgs[2] ) # int

        # fill in random radial value and dicrection
        spcdot_i3[ starIdx, 0 ] = speed[ randIdx ] # km/s

    return spcdot_i3 # km/s

#===============================================================================#
# termination conditions                                                        #
#===============================================================================#

def checkCollision(x_i3, r_i1):

    # find the pair-wise distance for each body
    x_ij = pairwiseDistance( x_i3 ) # ly

    # find the pair-wise sum of radii
    r_ij = r_i1 + r_i1.T # ly
    # convert diagonal to 0, since these pairs are not viable sim pairs
    np.fill_diagonal( r_ij, 0 )

    # determine any collitions
    collisions = ( r_ij > x_ij ) # ly
    return np.any( collisions ) # bool

def checkEjection(x_i3, xdot_i3, m_i1):

    # determine the escape velocity from the system for each body
    vEscape_i1 = escapeSpeed( x_i3, m_i1 ) # km/s

    # calculate the speed of each body
    speed_i1 = np.sqrt( ( xdot_i3**2 ).sum( axis=1, keepdims=True ) ) # km/s

    # determine any eminent ejections
    ejections = ( speed_i1 > vEscape_i1 ) # km/s
    return np.any( ejections ) # bool
