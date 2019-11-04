
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

import pyFiles.Functions as fun
import pyFiles.Input as inp

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

from copy import deepcopy
import numpy as np
import pandas as pd
import pdb
import os

#===============================================================================#
# BaseClass definition                                                          #
#===============================================================================#

class BaseClass:

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__(self, name, *args, **kwargs):
        """
        use:
        instructions on how to perform basic construction for any class instance
        that inherits BaseClass. Will look for saved state based on name
        provided; if it finds a saved state, will load it. any items in **kwargs
        are added as attributes.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:
        name            str             instance name is used to save/load state
                                        as well as descriptive printing to
                                        terminal
        *args           tuple, str      column names to use as estimators, if
                                        metadata needs to be generated.

        kwargs:

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """

        # assign name as attribute
        self.name_ = name

        # take out any key word arguments which aren't desired as attributes
        kwargs1 = {}
        if 'verbose' in kwargs: kwargs1['verbose'] = kwargs.pop('verbose')
        if 'addTail' in kwargs: kwargs1['addTail'] = kwargs.pop('addTail')

        # look for any previously saved state and load it if it exists
        self.loadState(**kwargs1)

        # only generate metadata if it doesn't already exist
        if not hasattr(self, 'factors_'):
            self._generateColumnNames(*args, **kwargs1)

        # only generate a sample if it doesn't already exist
        if not hasattr(self, 'sample_'): self._getSample(**kwargs1)

        # only set if not already present
        if not hasattr(self, 'sampleRowIdx_'): self.sampleRowIdx_ = 0

        # only set if not already present
        if not hasattr(self, 'runComplete_'): self.runComplete_ = False

        # add any remaining kwargs as attributes, will override previous state
        # if any keys conflict
        self._dict2attributes(kwargs, message="Overriding Attributes", **kwargs1)

    #===========================================================================#
    # public methods                                                            #
    # any methods defined here will be able to be used directly by its          #
    # children, make sure any attributes added by the methods below are present #
    # in the child class.                                                       #
    #===========================================================================#

    def loadState(self, **kwargs):
        """
        use:
        looks for previously saved state and loads it into instance attributes
        if it exists.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """
        state = fun.fromPickle( f"data/{self.name_}.pkl", **kwargs )
        self._dict2attributes( state, message='Loading State:', **kwargs )

    def saveState(self, **kwargs):
        """
        use:
        saves the current state of the model instance into a pickle, which will
        automatically be loaded up by the constructor next time it is
        instantiated.

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """
        fun.toPickle( f"data/{self.name_}.pkl", self.__dict__, **kwargs )

    def run(self, **kwargs):
        while not self.runComplete_:
            # run the treatement for current treatement, specified by
            # sampleRowIdx
            self._runScenario(**kwargs)
            # increment sampleRowIdx
            self.sampleRowIdx_ += 1
            # evaluate run completion conditions, if the sample row index is
            # greater than the number of rows in sample_
            self.runComplete_ = (self.sampleRowIdx_ == self.sample_.shape[0])
            # save current state of sim model
            self.saveState()
        self.sample_.to_csv(f"data/{self.name_}.csv", index=False)

    #===========================================================================#
    # public methods                                                            #
    # any methods defined here need to be implemnted in the child class         #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # any methods defined here will be able to be used directly by its          #
    # children, make sure any attributes added by the methods below are present #
    # in the child class.                                                       #
    #===========================================================================#

    def _dict2attributes(self, dictionary, **kwargs):
        """
        use:
        saves every item in dictionary as an attribute

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:           type:           description:

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """

        addTail = kwargs['addTail'] if 'addTail' in kwargs else False

        fun.printDict( dictionary, **kwargs )
        if len( dictionary ) > 0:
            for key,value in dictionary.items():
                if addTail:
                    setattr( self, f"{key}_", value )
                else:
                    setattr( self, key, value )

    def _generateColumnNames(self, *args, **kwargs):
        """
        use:
        adds list of all columns, factor space columns, estimator columns,
        number of factors, and number of estimators

        ========================================================================
        input:          type:           description:
        ========================================================================
        args:           type:           description:
        *args           tuple, str      column name(s) of estimators

        kwargs:         type:           description:
        verbose         bool            flag to print, default = False

        ========================================================================
        output:         type:
        ========================================================================
        None            None
        """

        # estimators are the args provided or 'runTime' by default
        if len( args ) > 0:
            estimators = list( args )
        else:
            estimators = [ 'collide', 'eject', 'survive' ]

        # define monte carlo columns
        mc = [ 'treatmentN', 'monteCarloN' ]

        # grab the constant factors from Input
        constant = list( inp.constantFactors.keys() )

        # grab control fractors from Input
        control = list( inp.controlFactors.keys() )

        # grab the random factors from Input
        random = inp.randomFactors

        # create an empty list to hold misc sim values and final values
        sim = [ 'nSteps', 'runTime' ]
        # fill in the columns for final sim values
        for starIdx in range(3):
            for coordinateIdx in range(3):
                for name in [ 'pos', 'vel' ]:
                    colName = f"{name}_({starIdx},{coordinateIdx},-1)"
                    sim.append( colName )

        # make a column name collection
        self.colNames_ = {
            'all'           : constant + control + estimators + mc + random + sim,
            'constant'      : constant,
            'control'       : control,
            'estimators'    : estimators,
            'monteCarlo'    : mc,
            'random'        : random,
            'sample'        : mc + control + estimators,
            'sim'           : sim,
        }

    #===========================================================================#
    # semi-protected                                                            #
    # any methods defined here need to be implemnted in the child class         #
    #===========================================================================#

    def _runScenario(self, *args, **kwargs):
        NotImplemented

    #===========================================================================#
    # semi-private methods                                                      #
    # child class can only access theese methods, in whole or in part, by using #
    # super()                                                                   #
    #===========================================================================#
