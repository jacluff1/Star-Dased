
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

import numpy as np

#===============================================================================#
# conversions                                                                   #
#===============================================================================#

# solar radius to light year
sr2ly = 7.35355e-8
# parsec to light year
pc2ly = 3.26156
# meter to kilometer
m2km = 1e-3
# meter to light year
m2ly = 1.057e-16
# kilometer to lightyear
km2ly = 1.057e-13

# kilogram to solar mass
kg2solar = 5.02785e-31

# year to seconds
yr2s = 60 * 60 * 24 * 365.25
# 1000 years to seconds
kyr2s = yr2s * 1e3

#===============================================================================#
# constants                                                                     #
#===============================================================================#

# gravitational constant ( km/s )^2 ( ly )^1 ( solar mass )^-1
G = 6.67408e-11 * m2km**2 * m2ly / kg2solar

#===============================================================================#
# parameters                                                                    #
#===============================================================================#

# initial mass function parameters: alpha1, alpha2, m1, m2, m3
IMFparams = 1.3, 2.3, 0.08, 0.5, 100.0

# mass array for IMF PDF, the number density of stars (in solar mass)
IMFmass = np.linspace( 0.08, 100, 1000 )

# initial CM radius parameters
radiusParams = (
    # smallest placement radius = radius of smallest star ( light year )
    0.63 * sr2ly,
    # maximum placement radius ( light year )
    1.0 * pc2ly,
    # number of allowed positions
    18,
    )

# polar angle parameters
thetaParams = (
    # smallest angle ( radians )
    0.0,
    # largest angle ( radians )
    np.pi,
    # number of allowed positions
    18,
)

# azimuthal angle parameters
phiParams = (
    # smallest angle to allow ( radians )
    0.0,
    # largest angle to allow ( radians )
    2 * np.pi,
    # number of allowed positions
    18,
)

# mass parameters
massParams = (
    # minimum mass ( solar mass )
    0.08,
    # maximum mass ( solar mass )
    100,
    # number of allowed positions
    18,
)

# initial speed parameters
speedParams = (
    # minimum initial speed ( km/s )
    0.0,
    # maximum spped computed after placement in order to always start less than
    # escape velocity from the system
    # number of allowed positions
    100,
)

# max run time ( s )
maxT = 10 * kyr2s
