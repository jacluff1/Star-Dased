
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

# control factors
# (starIdx, coordinateIdx, timeIdx)
constantFactors = {
    'pos_(1,1,0)' : np.pi/2,    # star 1, initial theta pos (radians)
    'pos_(2,1,0)' : np.pi/2,    # star 2, initial theta pos (radians)
    'pos_(1,2,0)' : 0.0,        # star 1, initial phi pos (radians)
    'pos_(2,2,0)' : np.pi,      # star 2, initial phi pos (radians)
    'pos_(3,2,0)' : 0.0,        # star 3, initial phi pos (radians)
    'vel_(1,1,0)' : np.pi/2     # star 1, initial theta vel (radians)
    'vel_(2,1,0)' : np.pi/2     # star 2, initial theta vel (radians)
    'vel_(1,2,0)' : np.pi/2     # star 1, initial phi vel (radians)
    'vel_(2,2,0)' : (3/2)*np.pi # star 2, initial phi vel (radians)
    'vel_(3,2,0)' : np.pi/2     # star 3, initial phi vel (radians)
}

# random factors

# (starIdx, coordinateIdx, timeIdx)
# pos_(i,0,0), initial radial position parameters: min, max (ly)
radiusParams = ( 0.1 , 5.0 )

# (starIdx, coordinateIdx, timeIdx)
# pos_(3,2,0), polar angle parameters: min, max (radians)
thetaParams1 = ( 0 , (1/2)*np.pi )

# (starIdx)
# mass_(i), mass parameters: min, max (solar mass)
massParams = ( 0.08, 50 )

# (starIdx, coordinateIdx, timeIdx)
# vel_(3,2,0), polar angle parameters: min, max (radians)
thetaParams2 = ( (1/2)*np.pi, (3/2)*np.pi )

# max run time ( s )
maxT = 10 * kyr2s
