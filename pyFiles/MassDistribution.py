
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import Functions as fun
from Input import IMFparams, IMFmass

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pdb

#===============================================================================#
# initial mass funtion solutions                                                #
#===============================================================================#

def Kroupa_Salpeter_solve_ki( alpha1, alpha2, m1, m2, m3 ):
    """
    use:
    solve for normalization constants to Kroupa-Salpeter IMF.
    xi(m) = dN/dm = {
        m1 <= m <= m2   : k1 m^(-alpha1),
        m2 <= m <= m3   : k2 m^(-alpha2),
    }
    solving constants so that:
    (1) integral xi(m) dm from m1 to m3 = 1
    (2) k1 m1^(-alpha1) = k2 m2^(-alpha2)

    from condition (2), k1 = 2 k2
    solve for k2 using condition (1)

    reference:
    https://iopscience.iop.org/article/10.3847/2041-8213/aa970f

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    m1              float           lower limit of star mass range (solar mass)
    m2              float           intermidiary limit of star mass range
                                    (solar mass)
    m3              float           upper limit of star mass range (solar mass)
    alpha1          float           solved/fit parameter
    alpha2          float           solved/fit parameter

    kwargs:         type:           description:

    ============================================================================
    output:         type:
    ============================================================================
    k1,k2           tuple (floats)
    """
    denominator     = 2 * alpha1 * ( m1**(-alpha1-1) - m2**(-alpha1-1) )
    denominator    +=     alpha2 * ( m2**(-alpha2-1) - m3**(-alpha2-1) )
    k2 = 1 / denominator
    k1 = 2 * k2
    return k1, k2

def Kroupa_Salpeter( IMFparams, IMFmass ):
    """
    use:
    solution to compute IMF PDF (initial mass function - probability
    distribution function)
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    IMFparams       tuple           parameters to feed to IMF solution
    IMFmass         np.ndarray      mass - variable

    kwargs:         type:           description:

    ============================================================================
    output:         type:
    ============================================================================
    IMFpdf          np.ndarray
    """
    k1, k2  = Kroupa_Salpeter_solve_ki( *IMFparams )
    IMFpdf = ( k1 * IMFmass**(-IMFparams[0]) ) + ( k2 * IMFmass**(-IMFparams[1]) )
    return IMFpdf

#===============================================================================#
# generate IMF PDF                                                              #
#===============================================================================#

def generateStarIndices( N, **kwargs ):
    """
    use:
    generate an array of starClasses indices

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    N               int             how many indices to generate

    kwargs:         type:           description:

    ============================================================================
    output:         type:
    ============================================================================
    starIdx         np.ndarray
    """
    stars = pd.read_csv( "../data/starClass.txt" )
    return np.random.choice( stars.shape[0], p=stars.PDFweight.values, size=N )

def IMF( IMFparams, IMFmass, **kwargs ):
    """
    use:
    solution to compute IMF PDF (initial mass function - probability
    distribution function)
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    IMFparams       tuple           parameters to feed to IMF solution
    IMFmass         np.ndarray      mass - variable

    kwargs:         type:           description:
    IMFsolution     function        function to use to calculate IMF, default
                                    = Kroupa_Salpeter

    ============================================================================
    output:         type:
    ============================================================================
    IMFpdf          np.ndarray
    """
    IMFsolution = kwargs['IMFsolution'] if 'IMFsolution' in kwargs else Kroupa_Salpeter
    IMFpdf = IMFsolution( IMFparams, IMFmass )
    # normalize
    IMFpdf /= np.trapz( IMFpdf, x=IMFmass )
    return IMFpdf

def plotBar( **kwargs ):
    """
    use:
    plot histogram of PDF with defined spectral types

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    N               int             how many stars to plot distribution

    kwargs:         type:           description:
    grid            bool            flag to show grid on figure, default = False
    IMFsolution     function        solution to use, default = Kroupa_Salpeter
    N               int             number of star indicies to generate, default
                                    = 1000
    save            bool            flag to save plot, default = False
    show            bool            flag to show plot, default = True
    toFile          str             what to name the figure if saved,
                                    default = 'IMF_PDF_hist'
    verbose         bool            whether to print or not

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    grid        = kwargs['grid'       ] if 'grid'        in kwargs else False
    IMFsolution = kwargs['IMFsolution'] if 'IMFsolution' in kwargs else Kroupa_Salpeter
    N           = kwargs['N'          ] if 'N'           in kwargs else 1000
    save        = kwargs['save'       ] if 'save'        in kwargs else False
    show        = kwargs['show'       ] if 'show'        in kwargs else False
    toFile      = kwargs['toFile'     ] if 'toFile'      in kwargs else "IMF_PDF_bar"

    # generate star indicies
    N1 = generateStarIndices( N, **kwargs )
    # find the counts for each population of the generated sample
    N1 = np.bincount( N1 )
    # display counts in decimal percent
    N1 = N1 / N
    # convert to actual percent
    N1 *= 100

    title = f"{IMFsolution.__name__} Generated Sample".replace( "_", "-" )
    labels = [ 'O', 'B', 'A', 'F', 'G', 'K', 'M' ]

    fig = plt.figure( figsize=(15,15) )

    plt.title(  title           , fontsize=24 )
    plt.xlabel( "Spectral Class", fontsize=20 )
    plt.ylabel( "Percent (%)"   , fontsize=20 )

    plt.bar( np.arange(7), N1, tick_label=labels )

    for idx,label in enumerate( labels ):
        plt.annotate(
            f"{label}: {N1[idx]:0.1f} %"         ,
            xy       = ( idx - 0.3, N1[idx] + 2 ),
            color    = 'r'                       ,
            fontsize = 20
        )

    plt.tight_layout()
    if grid: plt.grid( True )

    if show: plt.show()
    if save: fun.saveFigure( toFile, fig, **kwargs )

def plotIMF( x, y, **kwargs ):
    """
    use:
    comput and plot IMF array

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    x               np.ndarray      IMFmass
    y               np.ndarray      IMFpdf

    kwargs:         type:           description:
    grid            bool            flag to show grid on figure, default = True
    IMFsolution     function        solution to use, default = Kroupa_Salpeter
    save            bool            flag to save plot, default = False
    show            bool            flag to show plot, default = True
    toFile          str             what to name the figure if saved,
                                    default = 'IMFpdf'
    verbose         bool            whether to print or not

    ============================================================================
    output:         type:
    ============================================================================
    None
    """

    # set variables from key word arguments
    grid        = kwargs['grid'       ] if 'grid'        in kwargs else True
    IMFsolution = kwargs['IMFsolution'] if 'IMFsolution' in kwargs else Kroupa_Salpeter
    save        = kwargs['save'       ] if 'save'        in kwargs else False
    show        = kwargs['show'       ] if 'show'        in kwargs else True
    toFile      = kwargs['toFile'     ] if 'toFile'      in kwargs else 'IMF_PDF'
    xlim        = kwargs['xlim'       ] if 'xlim'        in kwargs else (x[0], x[-1])

    title = f"{IMFsolution.__name__} IMF PDF".replace( "_", "-" )
    ylim = ( y[-1] - 1 , y[0] + 1 )

    fig = plt.figure( figsize=(15,15) )

    plt.title(  title                     , fontsize=24 )
    plt.xlabel( "Mass (M$_{\odot}$)"      , fontsize=20 )
    plt.ylabel( "N$_{star}$ / M$_{\odot}$", fontsize=20 )

    plt.plot( x, y, linewidth=3, color='b', label='PDF' )
    plt.vlines( 0.08, *ylim, color='r', linestyle=':', label='Chandrasekhar limit', linewidth=3 )

    plt.xlim( *xlim )
    plt.ylim( *ylim )
    plt.legend( loc='best' )
    plt.tight_layout()
    if grid: plt.grid( True )

    if show: plt.show()
    if save: fun.saveFigure( toFile, fig, **kwargs )

def stellarMassWeights( x, y, **kwargs ):
    """
    use:
    get the mass probability weights for each spectral type

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    x               np.ndarray      IMFmass
    y               np.ndarray      IMFpdf

    kwargs:         type:           description:
    verbose         bool            flag to print, default = False

    ============================================================================
    output:         type:
    ============================================================================
    None
    """
    stars   = pd.read_csv( "../data/starClass.txt" )

    for rowIdx in stars.index:

        # find final index from PDF for spectral type
        idxf = fun.findIdx( x, stars.loc[ rowIdx, 'mass' ] )

        if stars.loc[ rowIdx, 'class' ] == 'M':
            # integrate PDF for M-class star
            stars.loc[ rowIdx, 'PDFweight' ] = np.trapz( y[ : idxf ],
                x=x[ : idxf ] )
        else:
            # find the index for the starting point
            idx0 = fun.findIdx( x, stars.loc[ rowIdx+1, 'mass'] )
            # integrate PDF for all other star classes
            stars.loc[ rowIdx, 'PDFweight' ] = np.trapz( y[ idx0 : idxf ],
                x = x[ idx0 : idxf ] )

    # re-normalize
    stars.PDFweight /= stars.PDFweight.sum()

    stars.to_csv( "../data/starClass.txt", index=False )

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":

    kwargs = {
        'save'      : True,
        'verbose'   : True,
        'xlim'      : (-1,100),
    }

    x = IMFmass
    y = IMF( IMFparams, IMFmass )

    plotIMF( x, y, **kwargs )
    stellarMassWeights( x, y, **kwargs )
    #plotBar( **kwargs )
