
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

# constant factors
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

# control factors
# (starIdx, coordinateIdx, timeIdx)
controlFactors = {
    'pos_(1,0,0)'   : ( 0.1, 5.0 ), # star 1 initial radial position limits (ly)
    'pos_(2,0,0)'   : ( 0.1, 5.0 ), # star 2 initial radial position limits (ly)
    'pos_(3,0,0)'   : ( 0.1, 5.0 ), # star 3 initial radial position limits (ly)
    'pos_(3,1,0)'   : ( 0.0, np.pi/2 ), # star 3 initial polar pos angle limits (ly)
    'mass_(0)'      : ( 0.08, 50 ), # star 1 mass limits (solar mass)
    'mass_(1)'      : ( 0.08, 50 ), # star 2 mass limits (solar mass)
    'mass_(2)'      : ( 0.08, 50 ), # star 3 mass limits (solar mass)
    'vel_(3,1,0)'   : ( np.pi/2, (3/2)*np.pi ), # star 3 initial polar vel angle limits (radians)
}

# random factors
# (starIdx, coordinateIdx, timeIdx)
randomFactors = [
    'vel_(1,0,0)', # star 1 iniital speed (km/s)
    'vel_(2,0,0)', # star 2 initial speed (km/s)
    'vel_(3,0,0)', # star 3 initial speed (km/s)
]

# max run time ( s )
maxT = 10 * kyr2s
