
#===============================================================================#
# import internal dependencies                                                  #
#===============================================================================#

from pyFiles.BaseClass import BaseClass
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from MLbase import MLbase


#===============================================================================#
# import external dependencies                                                  #
#===============================================================================#

#===============================================================================#
# Simulation definition                                                         #
#===============================================================================#

class PolynomialRegression( BaseClass, MLbase ):

    #===========================================================================#
    # constructor                                                               #
    #===========================================================================#

    def __init__( self, *args, **kwargs ):
        pass

    #Note need to figure the index scheme or the resulting output sample structure that would be fed to the metaModels
    def run(self, *args, **kwargs ):
        poly_Features = PolynomialFeatures(degree=8) #Based on the number of features 
        x_poly = poly_Features.fit_transform(self.sample_) #Relating to the control factor columns
        
        poly_Features.fit(x_poly,self.sample_ )#Relating to the survival orbit column that is deduced from whether escape or collided
        lin = LinearRegression()
        lin.fit(X_poly,y);
        

    #===========================================================================#
    # puplic methods                                                            #
    #===========================================================================#

    #===========================================================================#
    # semi-protected methods                                                    #
    #===========================================================================#

    #===========================================================================#
    # semi-private methods                                                      #
    #===========================================================================#

#===============================================================================#
# main                                                                          #
#===============================================================================#

if __name__ == "__main__":
    poly = PolynomialRegression()
    poly.run()
