#!/bin/bash
# script tested on Ubuntu 18.04.3 LTS using Python 3.6.8

# activate StarDasedEnv
source activateEnv.sh

python -B pyFiles/Simulation.py
python -B pyFiles/Plots.py --positionPlot True --animation True
# python -B pyFiles/MetaModels/PolynomialRegression
# python -B pyFiles/MetaModels/RegressionBasisFunctions
python -B pyFiles/MetaModels/RFclassification.py
# python -B pyFiles/MetaModels/ArtificialNeuralNetwork
