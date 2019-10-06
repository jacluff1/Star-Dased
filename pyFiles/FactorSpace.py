
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from Input import radiusParams, thetaParams, phiParams

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

#===============================================================================#
# positions                                                                     #
#===============================================================================#

# construct allowable radii in the factor space. Log the rmin and rmax in order
# preserve physical number when converted to exponential
radii = np.linspace(
    np.log( radiusParams[0] ),
    np.log( radiusParams[1] ),
    radiusParams[2],
)
radii = np.exp( radii )

# construct allowable polar angles in the factor space
thetas = np.linspace( *thetaParams, endpoint=False )

# construct allowable azimuthal angles in the factor space
phis = np.linspace( *phiParams, endpoint=False )

#===============================================================================#
# generate factor space                                                         #
#===============================================================================#

"""
I'm thinking of doing this implenting this whole file in the Simulation
definition. I am thinking of doing a random walk starting from outer edges of
the factor space and from the center of the factor space.

Each run of the simulation will record the input and sim data for later
processing.
"""
