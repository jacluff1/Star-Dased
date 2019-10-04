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

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import os
import pickle

#===============================================================================#
# coordinate frames                                                             #
#===============================================================================#

def cartesian2spherical( *args ):
    """
    use:

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:

    kwargs:         type:           description:

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """
    pass

def spherical2cartesian( *args ):
    """
    use:

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:

    kwargs:         type:           description:

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """
    pass

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

    fromFile = f"../data/{fromFile}.pkl"

    if os.path.isfile( fromFile ):
        toObject = pickle.load(
            open( fromFile, 'rb' ) # read the byte file
        )
    else:
        toObject = {}

    return toObject

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
    verbose         bool            whether to actually print or not.
                                    default = False

    ============================================================================
    output:         type:
    ============================================================================
    None            None
    """

    verbose = kwargs['verbose'] if 'verbose' in kwargs else False

    if verbose:

        # package dictionary
        results = [ "\n\tresults\n\tkey:\tvalue\n\t============="]
        for key,value in dictionary.items():
            try:
                results.append( f"\t{key}:\t{value:0.2f}" )
            except ValueError:
                results.append( f"\t{key}:\t{value}" )
        printHeader( *results, **kwargs )

def printHeader( *args, **kwargs ):
    """
    use:
    prints a decorated section header with any optional provided arguments
    printed on a new line.

    ============================================================================
    input:          type:           description:
    ============================================================================
    args:           type:           description:
    message(s)      str             each provided argument gets printed in the
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
        for arg in args: print( arg )
        printBreak( **kwargs )
