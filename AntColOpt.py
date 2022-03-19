# IMPORT MODULES
import random
import sys
import pprint
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# FUNCTIONS
def generatePoint(xWidth, yWidth, numPoint): # Generates points to travel in 2D space
    # xWidth:   Horizontal length of 2D space, x = 1:xWidth
    # yWidth:   Vertical length of 2D space, y = 1:yWidth
    # numPoint: Number of points to generate in 2D space

    numMaxPoint = xWidth*yWidth # Maximum number of points 2D space can have 

    if numPoint > numMaxPoint:
        print("\nWARNING\nNumber of points to generate exceeds the maximum number of points 2D space can have.\nEXECUTION STOPPED.")
        sys.exit
        
    coordPoint = []
    # Create random coordinates for all points in 2D space
    xCoordArr = random.sample(range(1, xWidth + 1), numPoint)
    yCoordArr = random.sample(range(1, yWidth + 1), numPoint)
    for i in range(numPoint): 
        coordPoint.append((xCoordArr[i], yCoordArr[i]))

    return coordPoint

def calcDist(point1, point2): # Calculates the distance between given two points
    xDiff = abs(point1[0]-point2[0])
    yDiff = abs(point1[1]-point2[1])
    dist = np.sqrt(xDiff**2 + yDiff**2)
    return dist

def createProb(nextPointDist, nextPointPhe): # Create probability array based on next distance array and probability power (closer point higher probability)
    nextPointProb = np.power(nextPointDist, -1)
    #nextPointProb = np.divide(nextPointProb, sum(nextPointProb))
    nextPointProb = np.power(nextPointProb, distPow)
    #nextPointProb = np.divide(nextPointProb, sum(nextPointProb))
    nextPointProb = np.multiply(nextPointProb, np.power(nextPointPhe, phePow))
    nextPointProb = np.divide(nextPointProb, sum(nextPointProb))
    return nextPointProb

def selectNext(nextPointProb): # Select the next point based on probability distribution array
    nextPointProbSorted = np.sort(nextPointProb)
    probLim = random.random()
    nextPointProbSel = []
    for j in range(len(nextPointProbSorted)):
        nextPointProbSel.append(np.sum(nextPointProbSorted[0:j+1]))
    nextPointProbVal = nextPointProbSorted[np.array(nextPointProbSel)>=probLim][0]
    nextPointDistVal = nextPointDist[np.where(nextPointProb==nextPointProbVal)[0][0]]
    return nextPointDistVal

# APPLICATION
# Specify inputs
xWidth = 1000
yWidth = 1000
numPoint = 100
numAnt = 100
distPow = 4
phePow = 1
numStep = 200
evaPheRat = 0.3
# Generate points
coordPoint = generatePoint(xWidth, yWidth, numPoint)
# Create distance matrix for generated points
distMat = np.zeros((numPoint, numPoint))
for startIdx in range(numPoint):
    for targetIdx in range(numPoint):
        startPoint = coordPoint[startIdx]
        targetPoint = coordPoint[targetIdx]
        distMat[startIdx, targetIdx] = calcDist(startPoint, targetPoint)

# Create pheromone matrix for generated points
pheMat = np.ones((numPoint, numPoint))

# Select initial point to release ants
#initPoint = random.choice(coordPoint) # Select initial point
#initIdx = coordPoint.index(initPoint) # Get the index of initial point

# Release ants
antStepHist = []
minDistHist = []
for stepIdx in range(numStep):
    antTravel = []
    antDist = []
    for antIdx in range(numAnt):
        # Initialize ant location
        initPoint = random.choice(coordPoint) # Select initial point
        initIdx = coordPoint.index(initPoint) # Get the index of initial point
        currPoint = initPoint
        currIdx = initIdx
        # Assign initial location into array for storing
        currIdxHis = []
        currPointArr = []
        currIdxHis.append(currIdx)
        currPointArr.append(currPoint)
        # Travel ant
        totalDist = 0
        for i in range (numPoint - 1): # Travel an ant through all points
            # Get distance array from distance matrix for current point
            nextPointDistOri = distMat[currIdx, :]
            nextPointDist = np.delete(nextPointDistOri, currIdxHis) # Delete current and previously travelled points
            # Get pheromone array from pheromone matrix for current point
            nextPointPheOri = pheMat[currIdx, :]
            nextPointPhe = np.delete(nextPointPheOri, currIdxHis) # Delete current and previously travelled points
            # Create probability array based on next distance array and probability power (closer point higher probability)
            nextPointProb = createProb(nextPointDist, nextPointPhe)
            # Select the next point based on probability distribution
            nextPointDistVal = selectNext(nextPointProb)
            # Move the ant to the next selected point
            currIdx = np.where(nextPointDistOri==nextPointDistVal)[0][0]
            currIdxHis.append(currIdx)
            totalDist += nextPointDistVal
        # Return ant to home
        currIdxHis.append(initIdx)
        # Store ant travelling data
        antTravel.append(currIdxHis)
        antDist.append(totalDist)
        # Get minimum distance in this release of ants
        minDistInStep = min(antDist)    
    # Update minimum distance history array
    minDistHist.append(minDistInStep)
    print("Minimum distance: " + str(min(minDistHist)) + " / Step " + str(stepIdx + 1))
    # Evaporate pheromone
    pheMat = np.multiply(pheMat, 1-evaPheRat)
    # Update pheromone matrice based on total distance values each ant in the ant group travelled
    for i in range(len(antTravel)):
        for j in range(len(currIdxHis)-1):
            startIdx = antTravel[i][j]
            targetIdx = antTravel[i][j+1]
            pheMat[startIdx][targetIdx] += 1/antDist[i]
    antStepHist.append((antTravel, antDist))

# Get minimum distance path
minDist = min(minDistHist)
minDistStepIdx = minDistHist.index(minDist)
minDistAntIdx = antStepHist[minDistStepIdx][1].index(minDist)
minDistPathIdx = antStepHist[minDistStepIdx][0][minDistAntIdx]

# Plot minimum distance travel route
plt.xlim(0, xWidth)
plt.ylim(0, yWidth)
plt.plot(initPoint[0], initPoint[1], marker="o", markersize=20, markeredgecolor="red")
for i in range(len(minDistPathIdx)):
    point = coordPoint[minDistPathIdx[i]]
    x = point[0]
    y = point[1]
    plt.plot(x, y, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
    if i != len(minDistPathIdx) - 1:
        nextPoint = coordPoint[minDistPathIdx[i + 1]]
        plt.arrow(x, y, dx=nextPoint[0]-point[0], dy=nextPoint[1]-point[1], width=.12)
plt.show()
