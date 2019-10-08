
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class MLbase:

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__( self, *args, **kwargs ):
        pass

    #===========================================================================#
    # puplic methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # puplic methods                                                            #
    # required for BaseClass, implemented here                                  #
    #===========================================================================#

    def run( self, *args, **kwargs ):
        """
        use:
        Method shall include the general instructions to populate self.data_,
        including running through each random walk scenario set up in the
        sample. For sim models this means generating sim data; for meta models
        this means generating results from different model hyper-parameters,
        which is used to find the best set of hyper-parameters for the meta
        model.

        For all scenarios, this method will make sure the following are recorded
        on the appropriate row in self.data_:
        1) initial state factors
        2) any calculated or generated factors/input
        3) the output of the run

        After each scenario, the current model will be:
        1) the factorState will updated, if result is better than previous
        result
        2) the randomWalkCounter will either be incremented or reset to 0
        3) the model state will be saved ( self.saveState() )

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

        NotImplemented

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    # required for BaseClass, implemented here                                  #
    # directly inheritable by MLBase children                                   #
    #===========================================================================#

    def _generateEmptyData( self, **kwargs ):
        """
        use:
        Method shall add an empty pd.DataFrame, accessed by self.data_. the
        DataFrame will hold all the generated data from all the random walks
        from all the initial states defined in the generated sample ( found in
        self.sample_ )

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

    def _generateFactorSpace( self, *args, **kwargs ):
        """
        use:
        Method shall add a dictionary, accessed by self.factorSpace_, where the keys
        are the sampleFactors and the values are np.arrays of all allowed values
        included in the factor space.

        The keys in sampleFactors_ must remain constant, but it is allowed to
        adjust the factor space (for example, expand the factor space, narrow it
        down around a percieved richer space, etc..). Every time the model is
        instantiated, it will retain its previous runs and re-set up the factor
        space it is considering.

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

    def _generateSampleFactors( self, **kwargs ):
        """
        use:
        Method shall add a pd.DataFrame, accessed by self.sample_ that has columns:
        [ 'factor', 'minIdx', 'midIdx', 'maxIdx' ]
        The rows shall be the factors being considered in the hypercube defining
        the sample/factor space.

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

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#
